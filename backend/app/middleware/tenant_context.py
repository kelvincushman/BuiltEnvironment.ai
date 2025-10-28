"""
Tenant context middleware for multi-tenancy support.

This middleware extracts tenant information from JWT tokens and makes it
available throughout the request lifecycle for proper data isolation.
"""

from contextvars import ContextVar
from typing import Optional, Callable
from uuid import UUID

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..core.security import decode_token


# Context variable to store tenant_id for the current request
_tenant_context: ContextVar[Optional[str]] = ContextVar("tenant_context", default=None)


class TenantContext:
    """
    Tenant context manager for multi-tenant data isolation.

    Usage:
        In your endpoint:
        ```python
        tenant_id = get_tenant_context()
        # Use tenant_id to filter queries
        ```
    """

    @staticmethod
    def set(tenant_id: str) -> None:
        """Set tenant_id in context."""
        _tenant_context.set(tenant_id)

    @staticmethod
    def get() -> Optional[str]:
        """Get tenant_id from context."""
        return _tenant_context.get()

    @staticmethod
    def clear() -> None:
        """Clear tenant context."""
        _tenant_context.set(None)


def get_tenant_context() -> UUID:
    """
    Dependency to get tenant_id from context.

    Use this as a FastAPI dependency in endpoints that require tenant context:

    ```python
    @router.get("/projects")
    async def get_projects(
        tenant_id: UUID = Depends(get_tenant_context),
        db: AsyncSession = Depends(get_db),
    ):
        # tenant_id is automatically extracted from JWT token
        result = await db.execute(
            select(Project).where(Project.tenant_id == tenant_id)
        )
        return result.scalars().all()
    ```

    Returns:
        UUID: Tenant ID from context

    Raises:
        HTTPException: If tenant context is not set
    """
    tenant_id_str = TenantContext.get()

    if not tenant_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant context not found. Authentication required.",
        )

    try:
        return UUID(tenant_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID format",
        )


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract tenant_id from JWT token and set it in context.

    This middleware runs on every request and:
    1. Extracts the Authorization header
    2. Decodes the JWT token
    3. Extracts tenant_id from the token
    4. Sets it in the context for use by endpoints

    Endpoints that don't require authentication (like /register, /login, /health)
    can be excluded by configuring exempt_paths.
    """

    def __init__(
        self,
        app: ASGIApp,
        exempt_paths: Optional[list[str]] = None,
    ):
        """
        Initialize middleware.

        Args:
            app: ASGI application
            exempt_paths: List of paths that don't require tenant context
        """
        super().__init__(app)
        self.exempt_paths = exempt_paths or [
            "/health",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process request and extract tenant context.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain

        Returns:
            Response: HTTP response
        """
        # Clear any existing context
        TenantContext.clear()

        # Check if path is exempt from tenant context requirement
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # Extract Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            # No auth header - let the endpoint handle it
            # (some endpoints may be public)
            return await call_next(request)

        # Extract token from "Bearer <token>"
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return await call_next(request)
        except ValueError:
            # Invalid auth header format - let endpoint handle it
            return await call_next(request)

        # Decode token and extract tenant_id
        try:
            payload = decode_token(token)
            tenant_id = payload.get("tenant_id")

            if tenant_id:
                TenantContext.set(tenant_id)
        except HTTPException:
            # Token is invalid - let the endpoint handle it
            pass

        # Process request
        response = await call_next(request)

        # Clear context after request
        TenantContext.clear()

        return response


# Convenience function for checking tenant ownership
async def verify_tenant_access(
    resource_tenant_id: UUID,
    current_tenant_id: UUID = None,
) -> None:
    """
    Verify that the current tenant has access to a resource.

    Usage:
        ```python
        @router.get("/projects/{project_id}")
        async def get_project(
            project_id: UUID,
            tenant_id: UUID = Depends(get_tenant_context),
            db: AsyncSession = Depends(get_db),
        ):
            result = await db.execute(
                select(Project).where(Project.id == project_id)
            )
            project = result.scalar_one_or_none()

            if not project:
                raise HTTPException(404, "Project not found")

            # Verify tenant access
            await verify_tenant_access(project.tenant_id, tenant_id)

            return project
        ```

    Args:
        resource_tenant_id: Tenant ID of the resource being accessed
        current_tenant_id: Tenant ID from JWT token (usually from Depends(get_tenant_context))

    Raises:
        HTTPException: If tenant IDs don't match (403 Forbidden)
    """
    if current_tenant_id is None:
        current_tenant_id = get_tenant_context()

    if resource_tenant_id != current_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Resource belongs to a different tenant.",
        )

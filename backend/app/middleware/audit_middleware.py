"""
Audit middleware for automatically tracking API requests.

This middleware logs all API requests to the audit system with details about:
- Request method, path, and parameters
- User and tenant information (from JWT)
- Response status and timing
- Errors and exceptions
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..services.audit_logger import audit_logger
from ..models.audit import EventType
from ..middleware.tenant_context import TenantContext
from ..core.security import decode_token


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically audit all API requests.

    This middleware:
    1. Extracts user/tenant information from JWT token
    2. Times the request
    3. Logs the request to the audit system
    4. Captures errors if they occur
    """

    def __init__(
        self,
        app: ASGIApp,
        exempt_paths: list[str] = None,
    ):
        """
        Initialize audit middleware.

        Args:
            app: ASGI application
            exempt_paths: Paths to exclude from auditing
        """
        super().__init__(app)
        self.exempt_paths = exempt_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
        ]

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process request and log to audit system.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain

        Returns:
            Response: HTTP response
        """
        # Skip auditing for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # Extract user and tenant information from token
        user_id = None
        tenant_id = None
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                payload = decode_token(token)
                user_id = payload.get("sub")
                tenant_id = payload.get("tenant_id")
            except Exception:
                # Token invalid or expired - continue without user info
                pass

        # Start timing
        start_time = time.time()

        # Process request
        status_code = 500
        error_message = None

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as e:
            status_code = 500
            error_message = str(e)
            raise
        finally:
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Determine event type based on path
            event_type = self._determine_event_type(request.url.path)

            # Determine status
            if status_code >= 500:
                status = "failure"
            elif status_code >= 400:
                status = "error"
            else:
                status = "success"

            # Log the request (if we have tenant_id)
            if tenant_id:
                try:
                    description = f"{request.method} {request.url.path}"
                    if error_message:
                        description += f" - Error: {error_message}"

                    await audit_logger.log_event(
                        tenant_id=uuid.UUID(tenant_id),
                        event_type=event_type,
                        action=request.method.lower(),
                        actor_type="user" if user_id else "anonymous",
                        actor_id=user_id,
                        user_id=uuid.UUID(user_id) if user_id else None,
                        status=status,
                        description=description,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        ai_metadata={
                            "path": request.url.path,
                            "method": request.method,
                            "status_code": status_code,
                            "response_time_ms": response_time_ms,
                            "query_params": dict(request.query_params),
                        },
                    )
                except Exception as e:
                    # Don't fail the request if audit logging fails
                    import logging
                    logging.error(f"Failed to log audit event: {e}")

    def _determine_event_type(self, path: str) -> EventType:
        """
        Determine event type based on request path.

        Args:
            path: Request path

        Returns:
            EventType enum value
        """
        if "/auth/" in path:
            return EventType.USER_AUTH
        elif "/documents/" in path:
            if "upload" in path:
                return EventType.DOCUMENT_UPLOAD
            else:
                return EventType.DOCUMENT_PROCESS
        elif "/ai/" in path or "/chat/" in path:
            return EventType.AI_ANALYSIS
        elif "/subscriptions/" in path:
            return EventType.SUBSCRIPTION
        else:
            return EventType.USER_ACTION

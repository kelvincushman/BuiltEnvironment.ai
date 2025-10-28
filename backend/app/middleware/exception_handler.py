"""
Global exception handler middleware for consistent error responses.

Provides:
- Structured error responses across all endpoints
- Automatic error logging with context
- HTTP status code mapping for common exceptions
- Security-safe error messages (no sensitive data leaks)
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Dict, Any
import traceback

from ..core.config import settings

logger = logging.getLogger(__name__)


class AppException(Exception):
    """
    Base application exception with structured error information.

    Use this for custom business logic errors with specific status codes.
    """
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "APP_ERROR",
        details: Dict[str, Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class TenantIsolationError(AppException):
    """Raised when a tenant isolation violation is detected."""
    def __init__(self, message: str = "Access denied: Resource belongs to different tenant"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="TENANT_ISOLATION_VIOLATION",
        )


class ResourceNotFoundError(AppException):
    """Raised when a requested resource is not found."""
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class SubscriptionLimitError(AppException):
    """Raised when subscription limits are exceeded."""
    def __init__(self, limit_type: str, current_value: int, max_value: int):
        super().__init__(
            message=f"Subscription limit exceeded: {limit_type}",
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            error_code="SUBSCRIPTION_LIMIT_EXCEEDED",
            details={
                "limit_type": limit_type,
                "current_value": current_value,
                "max_value": max_value,
            },
        )


class ValidationError(AppException):
    """Raised for business logic validation errors."""
    def __init__(self, message: str, field: str = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler that catches all unhandled exceptions.

    Returns consistent error structure:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable message",
            "details": {...},
            "request_id": "uuid"
        }
    }
    """
    # Generate request ID for tracking
    request_id = request.state.request_id if hasattr(request.state, "request_id") else "unknown"

    # Log exception with context
    logger.error(
        f"Exception in {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        },
        exc_info=True,
    )

    # Build error response based on exception type
    error_response = _build_error_response(exc, request_id)

    return JSONResponse(
        status_code=error_response["status_code"],
        content={"error": error_response["error"]},
    )


def _build_error_response(exc: Exception, request_id: str) -> Dict[str, Any]:
    """Build structured error response based on exception type."""

    # Custom application exceptions
    if isinstance(exc, AppException):
        return {
            "status_code": exc.status_code,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
            },
        }

    # Starlette HTTP exceptions (raised by FastAPI)
    if isinstance(exc, StarletteHTTPException):
        return {
            "status_code": exc.status_code,
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": {},
                "request_id": request_id,
            },
        }

    # Request validation errors (Pydantic)
    if isinstance(exc, RequestValidationError):
        return {
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"validation_errors": exc.errors()},
                "request_id": request_id,
            },
        }

    # Database integrity errors (duplicate keys, foreign key violations)
    if isinstance(exc, IntegrityError):
        # Parse constraint name to provide better error message
        error_message = "Database integrity constraint violated"
        if "duplicate key" in str(exc).lower():
            error_message = "Resource already exists"
        elif "foreign key" in str(exc).lower():
            error_message = "Referenced resource does not exist"

        return {
            "status_code": status.HTTP_409_CONFLICT,
            "error": {
                "code": "INTEGRITY_ERROR",
                "message": error_message,
                "details": {} if settings.ENVIRONMENT == "production" else {"db_error": str(exc)},
                "request_id": request_id,
            },
        }

    # Database operational errors (connection issues)
    if isinstance(exc, OperationalError):
        return {
            "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Database service temporarily unavailable",
                "details": {},
                "request_id": request_id,
            },
        }

    # Catch-all for unexpected exceptions
    # In production, hide internal error details
    error_details = {}
    if settings.ENVIRONMENT != "production":
        error_details = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    return {
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": error_details,
            "request_id": request_id,
        },
    }


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handler specifically for HTTP exceptions."""
    return await global_exception_handler(request, exc)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler specifically for validation exceptions."""
    return await global_exception_handler(request, exc)

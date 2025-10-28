"""
FastAPI application entry point for BuiltEnvironment.ai
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import uuid

from .core.config import settings
from .db.base import init_db, close_db
from .api.v1.api import api_router
from .middleware.tenant_context import TenantContextMiddleware
from .middleware.audit_middleware import AuditMiddleware
from .middleware.rate_limiter import RateLimitMiddleware, rate_limiter
from .middleware.exception_handler import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from .services.audit_logger import audit_logger
from .services.rag_service import rag_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Initialize database
    await init_db()
    print("✅ Database initialized")

    # Startup: Start audit logger
    await audit_logger.start()
    print("✅ Audit logger started")

    # Startup: Initialize RAG service (ChromaDB connection)
    await rag_service.initialize()
    print("✅ RAG service initialized")

    # Startup: Initialize rate limiter (Redis connection)
    await rate_limiter.initialize()
    print("✅ Rate limiter initialized")

    yield

    # Shutdown: Close rate limiter
    await rate_limiter.close()
    print("👋 Rate limiter closed")

    # Shutdown: Stop RAG service
    await rag_service.shutdown()
    print("👋 RAG service shutdown")

    # Shutdown: Stop audit logger and flush events
    await audit_logger.stop()
    print("👋 Audit logger stopped")

    # Shutdown: Close database connections
    await close_db()
    print("👋 Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered building compliance and documentation platform",
    lifespan=lifespan,
)

# Register global exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


# Request ID middleware for tracking
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request for tracking."""
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware (before auth to protect all endpoints)
app.add_middleware(RateLimitMiddleware)

# Add tenant context middleware for multi-tenancy
app.add_middleware(TenantContextMiddleware)

# Add audit middleware for request tracking
app.add_middleware(AuditMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    """
    Comprehensive health check endpoint.

    Checks status of all critical services:
    - Database (PostgreSQL)
    - Cache (Redis)
    - Vector DB (ChromaDB)
    - OCR Service (DeepSeek-OCR)
    - RAG Service
    """
    from sqlalchemy import text
    from .db.base import get_db
    import httpx

    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {},
    }

    overall_healthy = True

    # Check Database
    try:
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            health_status["services"]["database"] = {
                "status": "healthy",
                "type": "postgresql",
            }
            break
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        overall_healthy = False

    # Check Redis (Cache)
    try:
        if rate_limiter.redis_client:
            await rate_limiter.redis_client.ping()
            health_status["services"]["redis"] = {
                "status": "healthy",
                "type": "cache",
            }
        else:
            health_status["services"]["redis"] = {
                "status": "not_configured",
            }
    except Exception as e:
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        overall_healthy = False

    # Check ChromaDB (Vector Database)
    try:
        if rag_service.chroma:
            # Try to list collections (lightweight operation)
            await rag_service.chroma.list_collections()
            health_status["services"]["chromadb"] = {
                "status": "healthy",
                "type": "vector_database",
                "collections": len(rag_service.chroma._collections),
            }
        else:
            health_status["services"]["chromadb"] = {
                "status": "not_initialized",
            }
    except Exception as e:
        health_status["services"]["chromadb"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        overall_healthy = False

    # Check DeepSeek-OCR Service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.DEEPSEEK_OCR_URL}/health")
            if response.status_code == 200:
                health_status["services"]["deepseek_ocr"] = {
                    "status": "healthy",
                    "type": "ocr_service",
                }
            else:
                health_status["services"]["deepseek_ocr"] = {
                    "status": "unhealthy",
                    "http_status": response.status_code,
                }
                overall_healthy = False
    except Exception as e:
        health_status["services"]["deepseek_ocr"] = {
            "status": "unreachable",
            "error": str(e),
        }
        # Don't mark overall as unhealthy - OCR is not critical

    # Set overall status
    health_status["status"] = "healthy" if overall_healthy else "degraded"

    # Return appropriate HTTP status
    status_code = 200 if overall_healthy else 503

    from fastapi.responses import JSONResponse

    return JSONResponse(content=health_status, status_code=status_code)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

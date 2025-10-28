"""
FastAPI application entry point for BuiltEnvironment.ai
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .db.base import init_db, close_db
from .api.v1.api import api_router
from .middleware.tenant_context import TenantContextMiddleware
from .middleware.audit_middleware import AuditMiddleware
from .services.audit_logger import audit_logger


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

    yield

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

"""
API v1 router that combines all endpoint routers.
"""

from fastapi import APIRouter
from .endpoints import auth_router

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Add more routers here as we build them:
# api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
# api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
# api_router.include_router(ai_router, prefix="/ai", tags=["AI Agents"])

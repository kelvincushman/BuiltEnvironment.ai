"""
API v1 router that combines all endpoint routers.
"""

from fastapi import APIRouter
from .endpoints.auth import router as auth_router
from .endpoints.projects import router as projects_router
from .endpoints.documents import router as documents_router

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])

# Add more routers here as we build them:
# api_router.include_router(ai_router, prefix="/ai", tags=["AI Agents"])
# api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
# api_router.include_router(compliance_router, prefix="/compliance", tags=["Compliance"])

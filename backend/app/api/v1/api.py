"""
API v1 router that combines all endpoint routers.
"""

from fastapi import APIRouter
from .endpoints.auth import router as auth_router
from .endpoints.projects import router as projects_router
from .endpoints.documents import router as documents_router
from .endpoints.chat import router as chat_router
from .endpoints.ai import router as ai_router
from .endpoints.subscriptions import router as subscriptions_router
from .endpoints.webhooks.stripe import router as stripe_webhook_router
from .endpoints.audit import router as audit_router

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(subscriptions_router, prefix="/subscriptions", tags=["Subscriptions"])
api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI Agents"])
api_router.include_router(audit_router, prefix="/audit", tags=["Audit"])

# Webhook endpoints (no auth prefix, different path structure)
api_router.include_router(stripe_webhook_router, prefix="/webhooks", tags=["Webhooks"])

# Future endpoints:
# api_router.include_router(compliance_router, prefix="/compliance", tags=["Compliance"])
# api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])

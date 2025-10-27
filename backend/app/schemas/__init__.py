"""
Pydantic schemas for API request/response validation.
"""

from .auth import (
    Token,
    TokenData,
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
)
from .user import User, UserCreate, UserUpdate
from .tenant import Tenant, TenantCreate, TenantUpdate
from .project import Project, ProjectCreate, ProjectUpdate
from .document import Document, DocumentCreate, DocumentUpdate

__all__ = [
    # Auth
    "Token",
    "TokenData",
    "RegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    # Tenant
    "Tenant",
    "TenantCreate",
    "TenantUpdate",
    # Project
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    # Document
    "Document",
    "DocumentCreate",
    "DocumentUpdate",
]

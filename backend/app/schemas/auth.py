"""
Pydantic schemas for authentication.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""

    user_id: str
    email: str
    tenant_id: str
    role: str


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """Registration request schema."""

    # Tenant information
    company_name: str = Field(..., min_length=2, max_length=255)
    company_email: EmailStr

    # User information
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "ABC Construction Ltd",
                "company_email": "info@abcconstruction.com",
                "first_name": "John",
                "last_name": "Smith",
                "email": "john.smith@abcconstruction.com",
                "password": "SecurePass123!",
                "phone": "+44 20 1234 5678",
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request schema."""

    token: str
    new_password: str = Field(..., min_length=8)


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str

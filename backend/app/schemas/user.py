"""
Pydantic schemas for user endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    job_title: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8)
    tenant_id: UUID


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    job_title: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """Schema for changing password."""

    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class User(UserBase):
    """User response schema."""

    id: UUID
    tenant_id: UUID
    is_active: bool
    is_verified: bool
    is_engineer: bool
    engineer_registration_number: Optional[str]
    engineer_qualification: Optional[str]
    role: str
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True

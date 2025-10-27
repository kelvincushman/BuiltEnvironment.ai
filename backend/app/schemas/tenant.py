"""
Pydantic schemas for tenant endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class TenantBase(BaseModel):
    """Base tenant schema with common fields."""

    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    country: str = "United Kingdom"


class TenantCreate(TenantBase):
    """Schema for creating a new tenant."""

    pass


class TenantUpdate(BaseModel):
    """Schema for updating tenant information."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None


class Tenant(TenantBase):
    """Tenant response schema."""

    id: UUID
    slug: str
    is_active: bool
    is_trial: bool
    max_users: int
    max_projects: int
    max_storage_gb: int
    created_at: datetime
    trial_ends_at: Optional[datetime]

    class Config:
        from_attributes = True

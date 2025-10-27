"""
Pydantic schemas for project endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class ProjectBase(BaseModel):
    """Base project schema with common fields."""

    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    reference_number: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    country: str = "United Kingdom"
    project_type: Optional[str] = None
    building_use: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating project information."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    reference_number: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    project_type: Optional[str] = None
    building_use: Optional[str] = None


class Project(ProjectBase):
    """Project response schema."""

    id: UUID
    tenant_id: UUID
    status: str
    compliance_summary: Dict[str, Any]
    engineer_validated: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

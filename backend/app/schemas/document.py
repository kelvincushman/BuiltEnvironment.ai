"""
Pydantic schemas for document endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class DocumentBase(BaseModel):
    """Base document schema with common fields."""

    original_filename: str
    document_type: Optional[str] = "other"


class DocumentCreate(DocumentBase):
    """Schema for creating a new document (after upload)."""

    project_id: UUID
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    file_extension: str


class DocumentUpdate(BaseModel):
    """Schema for updating document metadata."""

    document_type: Optional[str] = None
    engineer_notes: Optional[str] = None


class Document(DocumentBase):
    """Document response schema."""

    id: UUID
    tenant_id: UUID
    project_id: UUID
    filename: str
    file_size: int
    mime_type: str
    file_extension: str
    document_type: str
    status: str
    page_count: Optional[int]
    ai_analysis: Dict[str, Any]
    compliance_findings: Dict[str, Any]
    vector_indexed: Optional[Dict[str, Any]]
    engineer_notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True

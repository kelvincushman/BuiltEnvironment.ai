"""
Pydantic schemas for document endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from ..models.document import DocumentType, DocumentStatus


class DocumentBase(BaseModel):
    """Base document schema with common fields."""

    original_filename: str
    document_type: DocumentType = DocumentType.OTHER


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

    document_type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None
    engineer_notes: Optional[str] = None


class Document(DocumentBase):
    """Document response schema."""

    id: UUID
    tenant_id: UUID
    project_id: UUID
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    file_extension: str
    document_type: DocumentType
    status: DocumentStatus
    extracted_text: Optional[str] = None
    page_count: Optional[int] = None
    ai_analysis: Dict[str, Any] = {}
    compliance_findings: Dict[str, Any] = {}
    vector_indexed: Optional[Dict[str, Any]] = None
    engineer_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """Paginated list of documents."""

    documents: list[Document]
    total: int
    skip: int
    limit: int


class DocumentUploadResponse(BaseModel):
    """Response after successful document upload."""

    document: Document
    message: str = "Document uploaded successfully"
    extraction_status: str  # "success", "partial", "failed", "pending"
    pages_extracted: Optional[int] = None


class DocumentAnalysisRequest(BaseModel):
    """Request to analyze a document with AI."""

    agents: list[str] = Field(
        default=["fire_safety", "structural", "accessibility"],
        description="List of AI agents to run on this document"
    )
    priority: str = Field(default="normal", pattern="^(low|normal|high)$")


class DocumentAnalysisResponse(BaseModel):
    """Response from document analysis."""

    document_id: UUID
    status: str  # "queued", "processing", "completed", "failed"
    agents_queued: list[str]
    estimated_time_seconds: Optional[int] = None
    message: str

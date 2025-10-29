"""
Pydantic schemas for compliance findings.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from ..models.finding import FindingType, FindingSeverity, FindingStatus


class FindingBase(BaseModel):
    """Base finding schema."""

    finding_type: FindingType
    severity: FindingSeverity
    category: str = Field(..., max_length=100, description="Regulation category (e.g., 'Part B - Fire Safety')")
    regulation_reference: Optional[str] = Field(None, max_length=255, description="Specific regulation reference")
    standard_reference: Optional[str] = Field(None, max_length=255, description="British Standard reference")
    title: str = Field(..., max_length=500, description="Finding title")
    description: str = Field(..., description="Detailed description")
    recommendation: Optional[str] = Field(None, description="Recommended action")
    page_number: Optional[int] = Field(None, ge=1, description="Page number in document")
    section: Optional[str] = Field(None, max_length=255, description="Document section")
    line_number: Optional[int] = Field(None, ge=1, description="Line number in document")


class FindingCreate(FindingBase):
    """Schema for creating a finding."""

    document_id: UUID
    specialist_agent: str = Field(..., max_length=100, description="AI agent that created this finding")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence (0-1)")
    ai_reasoning: Optional[str] = Field(None, description="Why the AI flagged this")
    source_chunks: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="RAG source chunks")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class FindingUpdate(BaseModel):
    """Schema for updating a finding."""

    status: Optional[FindingStatus] = None
    severity: Optional[FindingSeverity] = None
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    recommendation: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Finding(FindingBase):
    """Finding response schema."""

    id: UUID
    tenant_id: UUID
    project_id: UUID
    document_id: UUID
    status: FindingStatus
    specialist_agent: str
    confidence_score: Optional[float]
    ai_reasoning: Optional[str]
    source_chunks: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class FindingsList(BaseModel):
    """Paginated findings list response."""

    findings: List[Finding]
    total: int
    page: int
    page_size: int
    pages: int


class FindingsSummary(BaseModel):
    """Summary statistics for findings."""

    total_findings: int
    by_severity: Dict[str, int]  # {"critical": 3, "major": 12, "minor": 45, "info": 8}
    by_status: Dict[str, int]    # {"open": 50, "in_review": 10, "resolved": 5, "dismissed": 3}
    by_category: Dict[str, int]  # {"Part B - Fire Safety": 15, "Part A - Structure": 10, ...}
    by_agent: Dict[str, int]     # {"fire_safety": 20, "structural_engineering": 15, ...}

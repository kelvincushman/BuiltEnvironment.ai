"""
Document model for uploaded building documents.
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from ..db.base import Base


class DocumentType(str, enum.Enum):
    """Document type classification."""

    ARCHITECTURAL = "architectural"
    STRUCTURAL = "structural"
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    FIRE_SAFETY = "fire_safety"
    ACCESSIBILITY = "accessibility"
    BUILDING_CONTROL = "building_control"
    TECHNICAL_SPEC = "technical_spec"
    REPORT = "report"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    """Document processing status."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    AI_ANALYSIS_COMPLETE = "ai_analysis_complete"
    READY_FOR_REVIEW = "ready_for_review"
    ENGINEER_REVIEW = "engineer_review"
    VALIDATED = "validated"
    ERROR = "error"


class Document(Base):
    """
    Document model for uploaded building documents.
    Stores metadata, AI analysis results, and compliance findings.
    """

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)

    # File details
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    mime_type = Column(String(100), nullable=False)
    file_extension = Column(String(10), nullable=False)

    # Document classification
    document_type = Column(SQLEnum(DocumentType), default=DocumentType.OTHER)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED)

    # Extracted content
    extracted_text = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)

    # AI Analysis results
    ai_analysis = Column(JSONB, default={})
    """
    Example structure:
    {
        "agents_used": ["fire_safety", "structural", "accessibility"],
        "confidence_score": 0.89,
        "document_summary": "Fire safety strategy for 5-storey residential building...",
        "key_findings": [...],
        "timestamp": "2025-10-27T10:00:00Z"
    }
    """

    # Compliance findings
    compliance_findings = Column(JSONB, default={})
    """
    Example structure:
    {
        "overall_status": "amber",
        "findings": [
            {
                "regulation": "Part B - Fire Safety",
                "requirement": "B1 - Means of warning and escape",
                "status": "green",
                "confidence": 0.95,
                "evidence": "Document section 3.2 specifies...",
                "page_references": [5, 6, 7]
            }
        ],
        "green_count": 15,
        "amber_count": 3,
        "red_count": 1
    }
    """

    # RAG/Vector database integration
    vector_indexed = Column(JSONB, default=None, nullable=True)
    """
    Example structure when indexed:
    {
        "collection_id": "chroma_collection_id",
        "chunk_count": 42,
        "indexed_at": "2025-10-27T10:05:00Z",
        "embedding_model": "text-embedding-3-small"
    }
    """

    # Engineer validation (inherits from project but can be document-specific)
    engineer_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant")
    project = relationship("Project", back_populates="documents")

    def __repr__(self):
        return f"<Document {self.original_filename} ({self.status.value})>"

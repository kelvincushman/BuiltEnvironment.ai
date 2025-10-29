"""
Project model for organizing documents and compliance work.
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from ..db.base import Base


class ProjectStatus(str, enum.Enum):
    """Project status enum."""

    DRAFT = "draft"
    IN_REVIEW = "in_review"
    AI_ANALYSIS_COMPLETE = "ai_analysis_complete"
    ENGINEER_REVIEW = "engineer_review"
    VALIDATED = "validated"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ARCHIVED = "archived"


class Project(Base):
    """
    Project model for organizing building projects.
    Each project contains multiple documents and compliance checks.
    """

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Project details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True)

    # Location
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    postcode = Column(String(20), nullable=True)
    country = Column(String(100), default="United Kingdom")

    # Project type
    project_type = Column(String(100), nullable=True)  # New Build, Refurbishment, Extension, etc.
    building_use = Column(String(100), nullable=True)  # Residential, Commercial, Industrial, etc.

    # Status
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)

    # Compliance summary (aggregated from documents)
    compliance_summary = Column(JSONB, default={})
    """
    Example structure:
    {
        "overall_status": "amber",
        "green_count": 45,
        "amber_count": 12,
        "red_count": 3,
        "regulations_checked": ["Part A", "Part B", "Part L"],
        "last_updated": "2025-10-27T10:00:00Z"
    }
    """

    # Engineer validation
    engineer_validated = Column(JSONB, default=None, nullable=True)
    """
    Example structure when validated:
    {
        "engineer_id": "uuid",
        "engineer_name": "John Smith",
        "engineer_registration": "CEng MCIBSE 12345",
        "validated_at": "2025-10-27T15:30:00Z",
        "digital_signature": "base64_encoded_signature",
        "comments": "All findings reviewed and validated."
    }
    """

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="project", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name} ({self.status.value})>"

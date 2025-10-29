"""
Finding model for storing AI compliance analysis results.

A finding represents an issue, recommendation, or observation
identified by the AI specialist agents during document analysis.
"""

import enum
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class FindingType(str, enum.Enum):
    """Types of findings."""

    COMPLIANCE_ISSUE = "compliance_issue"  # Regulatory non-compliance
    RECOMMENDATION = "recommendation"      # Improvement suggestion
    OBSERVATION = "observation"            # Neutral observation
    MISSING_INFO = "missing_info"         # Required information not found


class FindingSeverity(str, enum.Enum):
    """Severity levels for findings (traffic light system + info)."""

    CRITICAL = "critical"  # Red - Must be addressed immediately
    MAJOR = "major"        # Amber - Should be addressed
    MINOR = "minor"        # Green - Optional improvement
    INFO = "info"          # White - Informational only


class FindingStatus(str, enum.Enum):
    """Status of finding resolution."""

    OPEN = "open"           # Not yet addressed
    IN_REVIEW = "in_review" # Being reviewed
    RESOLVED = "resolved"   # Issue resolved
    DISMISSED = "dismissed" # Not applicable/false positive


class Finding(Base, TimestampMixin):
    """
    Finding from AI compliance analysis.

    Stores issues, recommendations, and observations identified
    by specialist agents during document analysis.
    """

    __tablename__ = "findings"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys (multi-tenant)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)

    # Finding classification
    finding_type = Column(SQLEnum(FindingType), nullable=False, index=True)
    severity = Column(SQLEnum(FindingSeverity), nullable=False, index=True)
    status = Column(SQLEnum(FindingStatus), nullable=False, default=FindingStatus.OPEN, index=True)

    # Regulation/standard reference
    category = Column(String(100), nullable=False, index=True)  # e.g., "Part B - Fire Safety"
    regulation_reference = Column(String(255))  # e.g., "Part B1 Section 3.2"
    standard_reference = Column(String(255))    # e.g., "BS 9999:2017"

    # Finding details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    recommendation = Column(Text)  # Suggested action

    # Document location
    page_number = Column(Integer)
    section = Column(String(255))
    line_number = Column(Integer)

    # AI metadata
    specialist_agent = Column(String(100), nullable=False, index=True)  # Which agent found it
    confidence_score = Column(Float)  # 0.0 to 1.0
    ai_reasoning = Column(Text)  # Why the AI flagged this

    # Source context (RAG chunks that led to this finding)
    source_chunks = Column(JSONB, default=list)  # List of {chunk_id, text, score}

    # Additional metadata
    metadata = Column(JSONB, default=dict)  # Extensible metadata field

    # Relationships
    tenant = relationship("Tenant", back_populates="findings")
    project = relationship("Project", back_populates="findings")
    document = relationship("Document", back_populates="findings")

    def __repr__(self):
        return f"<Finding {self.id}: {self.title} ({self.severity})>"

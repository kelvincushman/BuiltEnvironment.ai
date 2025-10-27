"""
Audit event model for tracking all system activities.
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from ..db.base import Base


class EventType(str, enum.Enum):
    """High-level event type categories."""

    USER_AUTH = "user.auth"
    USER_ACTION = "user.action"
    DOCUMENT_UPLOAD = "document.upload"
    DOCUMENT_PROCESS = "document.process"
    AI_ANALYSIS = "ai.analysis"
    AI_AGENT = "ai.agent"
    COMPLIANCE_CHECK = "compliance.check"
    ENGINEER_REVIEW = "engineer.review"
    SUBSCRIPTION = "subscription"
    SYSTEM = "system"


class AuditEvent(Base):
    """
    Audit event model for comprehensive activity tracking.
    Tracks user actions, AI agent activities, and system events.
    """

    __tablename__ = "audit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    # Event classification
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    action = Column(String(100), nullable=False)  # login, upload, analyze, validate, etc.
    status = Column(String(20), default="success")  # success, failure, pending

    # Event details
    description = Column(Text, nullable=True)
    resource_type = Column(String(50), nullable=True)  # document, project, user, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Actor (who performed the action)
    actor_type = Column(String(20), nullable=False)  # user, ai_agent, system
    actor_id = Column(String(255), nullable=True)  # user_id or agent name

    # AI-specific data
    ai_metadata = Column(JSONB, nullable=True)
    """
    Example structure for AI events:
    {
        "agent_type": "fire_safety",
        "agent_version": "1.0.0",
        "confidence_score": 0.89,
        "model_used": "claude-3-5-sonnet-20241022",
        "tokens_used": 5420,
        "processing_time_ms": 3200,
        "checkpoint_id": "langgraph_checkpoint_uuid",
        "findings_count": 18
    }
    """

    # Request metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="audit_events")
    user = relationship("User", back_populates="audit_events", foreign_keys=[user_id])

    def __repr__(self):
        return f"<AuditEvent {self.event_type.value}.{self.action} by {self.actor_type}>"

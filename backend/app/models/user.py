"""
User model for authentication and authorization.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..db.base import Base


class User(Base):
    """
    User model with multi-tenant support.
    Every user belongs to a tenant.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True)
    job_title = Column(String(100), nullable=True)

    # Professional credentials (for engineer validation)
    is_engineer = Column(Boolean, default=False)
    engineer_registration_number = Column(String(100), nullable=True)
    engineer_qualification = Column(String(255), nullable=True)  # CEng MCIBSE, CEng MICE, etc.

    # Role-based access control
    role = Column(String(50), default="user")  # user, admin, engineer, super_admin

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    conversations = relationship("Conversation", back_populates="user", foreign_keys="Conversation.user_id")
    audit_events = relationship("AuditEvent", back_populates="user", foreign_keys="AuditEvent.user_id")

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

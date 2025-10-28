"""
Tenant model for multi-tenancy.
Each tenant represents an organization/company using the platform.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..db.base import Base


class Tenant(Base):
    """
    Tenant model for multi-tenant architecture.
    Every user, project, and document belongs to a tenant.
    """

    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)

    # Contact information
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)

    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    postcode = Column(String(20), nullable=True)
    country = Column(String(100), default="United Kingdom")

    # Status
    is_active = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=True)

    # Limits (based on subscription tier)
    max_users = Column(Integer, default=3)
    max_projects = Column(Integer, default=5)
    max_storage_gb = Column(Integer, default=10)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    subscription = relationship(
        "Subscription", back_populates="tenant", uselist=False, cascade="all, delete-orphan"
    )
    projects = relationship("Project", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="tenant", cascade="all, delete-orphan")
    audit_events = relationship(
        "AuditEvent", back_populates="tenant", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Tenant {self.name} ({self.slug})>"

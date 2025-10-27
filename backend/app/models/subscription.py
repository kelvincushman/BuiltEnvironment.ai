"""
Subscription model for Stripe payment integration.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from ..db.base import Base


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum matching Stripe statuses."""

    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


class SubscriptionTier(str, enum.Enum):
    """Subscription tier enum matching pricing.json."""

    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Subscription(Base):
    """
    Subscription model integrated with Stripe.
    One subscription per tenant.
    """

    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, unique=True, index=True)

    # Stripe integration
    stripe_customer_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_price_id = Column(String(255), nullable=True)

    # Subscription details
    tier = Column(SQLEnum(SubscriptionTier), nullable=False, default=SubscriptionTier.STARTER)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.TRIALING)
    billing_cycle = Column(String(20), default="monthly")  # monthly or annual

    # Pricing
    amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    currency = Column(String(3), default="GBP")

    # Dates
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Usage tracking
    usage_data = Column(JSONB, default={})  # Store usage metrics as JSON

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="subscription")

    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]

    def __repr__(self):
        return f"<Subscription {self.tier.value} - {self.status.value}>"

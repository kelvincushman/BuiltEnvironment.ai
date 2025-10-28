"""
Pydantic schemas for subscription endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from ..models.subscription import SubscriptionStatus, SubscriptionTier


class SubscriptionBase(BaseModel):
    """Base subscription schema."""

    tier: SubscriptionTier
    billing_cycle: str = "monthly"  # monthly or annual


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a subscription."""

    payment_method_id: Optional[str] = None  # Stripe payment method ID


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription."""

    tier: Optional[SubscriptionTier] = None
    billing_cycle: Optional[str] = None


class Subscription(SubscriptionBase):
    """Subscription response schema."""

    id: UUID
    tenant_id: UUID
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    stripe_price_id: Optional[str]
    status: SubscriptionStatus
    amount: Decimal
    currency: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    canceled_at: Optional[datetime]
    ended_at: Optional[datetime]
    usage_data: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CheckoutSessionCreate(BaseModel):
    """Schema for creating a Stripe checkout session."""

    tier: SubscriptionTier
    billing_cycle: str = Field("monthly", pattern="^(monthly|annual)$")
    success_url: str
    cancel_url: str

    class Config:
        json_schema_extra = {
            "example": {
                "tier": "professional",
                "billing_cycle": "monthly",
                "success_url": "https://builtenvironment.ai/dashboard?success=true",
                "cancel_url": "https://builtenvironment.ai/pricing?canceled=true",
            }
        }


class CheckoutSessionResponse(BaseModel):
    """Response from creating a checkout session."""

    checkout_url: str
    session_id: str


class UsageStats(BaseModel):
    """Current usage statistics for a tenant."""

    projects_count: int
    projects_limit: int
    documents_count: int
    documents_limit: int
    storage_used_gb: float
    storage_limit_gb: int
    users_count: int
    users_limit: int
    ai_checks_this_month: int
    ai_checks_limit: Optional[int]  # None = unlimited

    @property
    def projects_percentage(self) -> float:
        """Calculate percentage of projects used."""
        if self.projects_limit == 0:
            return 0.0
        return (self.projects_count / self.projects_limit) * 100

    @property
    def storage_percentage(self) -> float:
        """Calculate percentage of storage used."""
        if self.storage_limit_gb == 0:
            return 0.0
        return (self.storage_used_gb / self.storage_limit_gb) * 100

    @property
    def users_percentage(self) -> float:
        """Calculate percentage of user seats used."""
        if self.users_limit == 0:
            return 0.0
        return (self.users_count / self.users_limit) * 100


class BillingHistory(BaseModel):
    """Billing history item."""

    id: str  # Stripe invoice ID
    date: datetime
    amount: Decimal
    currency: str
    status: str  # paid, open, void, uncollectible
    invoice_pdf: Optional[str]  # URL to invoice PDF
    description: str

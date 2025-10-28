"""
Subscription management endpoints for Stripe integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from ....db.base import get_db
from ....models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from ....models.tenant import Tenant
from ....schemas.subscription import (
    Subscription as SubscriptionSchema,
    CheckoutSessionCreate,
    CheckoutSessionResponse,
    UsageStats,
    BillingHistory,
)
from ....core.security import CurrentUser
from ....services.stripe_service import stripe_service
from ....services.usage_tracker import usage_tracker


router = APIRouter()


@router.get("/me", response_model=SubscriptionSchema)
async def get_my_subscription(
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current tenant's subscription information.
    """
    result = await db.execute(
        select(Subscription).where(
            Subscription.tenant_id == UUID(current_user.tenant_id)
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )

    return subscription


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionCreate,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a Stripe Checkout session for subscribing or upgrading.

    This creates a hosted Stripe Checkout page where users can enter
    their payment information and complete the subscription.
    """
    # Get tenant
    result = await db.execute(
        select(Tenant).where(Tenant.id == UUID(current_user.tenant_id))
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Get or create Stripe customer
    result = await db.execute(
        select(Subscription).where(Subscription.tenant_id == tenant.id)
    )
    subscription = result.scalar_one_or_none()

    if subscription and subscription.stripe_customer_id:
        customer_id = subscription.stripe_customer_id
    else:
        # Create new Stripe customer
        customer = await stripe_service.create_customer(
            email=tenant.email,
            name=tenant.name,
            tenant_id=str(tenant.id),
        )
        customer_id = customer.id

        # Update subscription with customer ID
        if subscription:
            subscription.stripe_customer_id = customer_id
            await db.commit()

    # Create checkout session
    try:
        session = await stripe_service.create_checkout_session(
            customer_id=customer_id,
            tier=request.tier,
            billing_cycle=request.billing_cycle,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            trial_days=14,  # TODO: Get from config
        )

        return CheckoutSessionResponse(
            checkout_url=session.url,
            session_id=session.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}",
        )


@router.post("/upgrade")
async def upgrade_subscription(
    tier: SubscriptionTier,
    billing_cycle: str,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Upgrade/downgrade subscription to a different tier.

    This immediately changes the subscription and prorates the charges.
    """
    # Only admins can modify subscriptions
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can modify subscriptions",
        )

    # Get subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.tenant_id == UUID(current_user.tenant_id)
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found. Please create a subscription first.",
        )

    # Update subscription in Stripe
    try:
        stripe_subscription = await stripe_service.update_subscription_tier(
            subscription_id=subscription.stripe_subscription_id,
            new_tier=tier,
            billing_cycle=billing_cycle,
            prorate=True,
        )

        # Sync with database
        updated_subscription = await stripe_service.sync_subscription_from_stripe(
            db=db,
            stripe_subscription=stripe_subscription,
        )

        return {"message": "Subscription updated successfully", "subscription": updated_subscription}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subscription: {str(e)}",
        )


@router.post("/cancel")
async def cancel_subscription(
    immediate: bool = False,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel subscription.

    Args:
        immediate: If True, cancel immediately. If False (default),
                  cancel at end of billing period.
    """
    # Only admins can cancel subscriptions
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can cancel subscriptions",
        )

    # Get subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.tenant_id == UUID(current_user.tenant_id)
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found",
        )

    # Cancel subscription in Stripe
    try:
        stripe_subscription = await stripe_service.cancel_subscription(
            subscription_id=subscription.stripe_subscription_id,
            cancel_at_period_end=not immediate,
        )

        # Sync with database
        updated_subscription = await stripe_service.sync_subscription_from_stripe(
            db=db,
            stripe_subscription=stripe_subscription,
        )

        cancel_message = (
            "Subscription canceled immediately"
            if immediate
            else f"Subscription will be canceled on {updated_subscription.current_period_end.strftime('%Y-%m-%d')}"
        )

        return {"message": cancel_message, "subscription": updated_subscription}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}",
        )


@router.post("/reactivate")
async def reactivate_subscription(
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Reactivate a canceled subscription (before period end).
    """
    # Only admins can reactivate subscriptions
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reactivate subscriptions",
        )

    # Get subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.tenant_id == UUID(current_user.tenant_id)
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No subscription found",
        )

    # Reactivate subscription in Stripe
    try:
        stripe_subscription = await stripe_service.reactivate_subscription(
            subscription_id=subscription.stripe_subscription_id,
        )

        # Sync with database
        updated_subscription = await stripe_service.sync_subscription_from_stripe(
            db=db,
            stripe_subscription=stripe_subscription,
        )

        return {"message": "Subscription reactivated successfully", "subscription": updated_subscription}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reactivate subscription: {str(e)}",
        )


@router.get("/billing-history", response_model=List[BillingHistory])
async def get_billing_history(
    limit: int = 10,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get billing history (invoices) for current tenant.
    """
    # Get subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.tenant_id == UUID(current_user.tenant_id)
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.stripe_customer_id:
        return []

    # Get invoices from Stripe
    try:
        invoices = await stripe_service.get_billing_history(
            customer_id=subscription.stripe_customer_id,
            limit=limit,
        )

        billing_history = [
            BillingHistory(
                id=invoice.id,
                date=invoice.created,
                amount=invoice.amount_paid / 100,  # Convert cents to pounds
                currency=invoice.currency.upper(),
                status=invoice.status,
                invoice_pdf=invoice.invoice_pdf,
                description=invoice.lines.data[0].description if invoice.lines.data else "Subscription",
            )
            for invoice in invoices
        ]

        return billing_history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve billing history: {str(e)}",
        )


@router.post("/customer-portal")
async def get_customer_portal(
    return_url: str,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get Stripe Customer Portal URL for managing subscription and billing.

    The Customer Portal allows users to:
    - Update payment method
    - View billing history
    - Download invoices
    - Manage subscription
    """
    # Get subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.tenant_id == UUID(current_user.tenant_id)
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No subscription found",
        )

    # Create portal session
    try:
        session = await stripe_service.create_customer_portal_session(
            customer_id=subscription.stripe_customer_id,
            return_url=return_url,
        )

        return {"portal_url": session.url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create customer portal session: {str(e)}",
        )


@router.get("/usage", response_model=UsageStats)
async def get_usage_stats(
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current usage statistics for tenant.

    Returns usage counts and limits for:
    - Projects
    - Documents
    - Storage (GB)
    - Users
    - AI compliance checks

    Use this to show usage dashboards and warn users when approaching limits.
    """
    try:
        stats = await usage_tracker.get_usage_stats(
            tenant_id=UUID(current_user.tenant_id),
            db=db,
        )
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage stats: {str(e)}",
        )

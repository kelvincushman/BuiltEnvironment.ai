"""
Stripe webhook handler for processing subscription events.

This endpoint receives webhook events from Stripe to keep subscription
status synchronized with our database.

Important events handled:
- customer.subscription.created
- customer.subscription.updated
- customer.subscription.deleted
- customer.subscription.trial_will_end
- invoice.payment_succeeded
- invoice.payment_failed
"""

from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import stripe
from datetime import datetime
import logging

from .....db.base import get_db
from .....models.subscription import Subscription, SubscriptionStatus
from .....models.tenant import Tenant
from .....services.stripe_service import stripe_service
from .....core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Stripe webhook events.

    Stripe sends webhook events to notify us of subscription changes.
    This keeps our database synchronized with Stripe's records.

    Security: Stripe signs each webhook with a secret. We verify the
    signature before processing to ensure the event came from Stripe.
    """
    # Get raw body and signature
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature header",
        )

    # Verify webhook signature
    try:
        event = stripe_service.verify_webhook_signature(
            payload=payload,
            signature=sig_header,
            webhook_secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid webhook signature: {e}",
        )

    # Log event
    logger.info(f"Received Stripe webhook event: {event.type} ({event.id})")

    # Handle different event types
    try:
        if event.type == "customer.subscription.created":
            await handle_subscription_created(db, event.data.object)
        elif event.type == "customer.subscription.updated":
            await handle_subscription_updated(db, event.data.object)
        elif event.type == "customer.subscription.deleted":
            await handle_subscription_deleted(db, event.data.object)
        elif event.type == "customer.subscription.trial_will_end":
            await handle_trial_will_end(db, event.data.object)
        elif event.type == "invoice.payment_succeeded":
            await handle_payment_succeeded(db, event.data.object)
        elif event.type == "invoice.payment_failed":
            await handle_payment_failed(db, event.data.object)
        else:
            logger.info(f"Unhandled event type: {event.type}")

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing webhook event {event.type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {e}",
        )


async def handle_subscription_created(
    db: AsyncSession,
    stripe_subscription: stripe.Subscription,
):
    """
    Handle subscription.created event.

    This is fired when a new subscription is created (after checkout).
    """
    logger.info(f"Processing subscription.created: {stripe_subscription.id}")

    # Sync subscription to database
    try:
        await stripe_service.sync_subscription_from_stripe(
            db=db,
            stripe_subscription=stripe_subscription,
        )
        logger.info(f"Subscription {stripe_subscription.id} synced successfully")
    except ValueError as e:
        logger.warning(f"Subscription not found in database: {e}")
        # Subscription might be created via webhook before our database entry exists
        # This can happen with the checkout flow


async def handle_subscription_updated(
    db: AsyncSession,
    stripe_subscription: stripe.Subscription,
):
    """
    Handle subscription.updated event.

    This is fired when subscription details change (tier, status, etc.).
    """
    logger.info(f"Processing subscription.updated: {stripe_subscription.id}")

    # Sync subscription to database
    try:
        subscription = await stripe_service.sync_subscription_from_stripe(
            db=db,
            stripe_subscription=stripe_subscription,
        )

        # Update tenant status based on subscription
        if subscription.status == SubscriptionStatus.ACTIVE:
            result = await db.execute(
                select(Tenant).where(Tenant.id == subscription.tenant_id)
            )
            tenant = result.scalar_one_or_none()
            if tenant:
                tenant.is_active = True
                tenant.is_trial = False
                await db.commit()

        logger.info(f"Subscription {stripe_subscription.id} updated successfully")
    except ValueError as e:
        logger.error(f"Failed to sync subscription: {e}")


async def handle_subscription_deleted(
    db: AsyncSession,
    stripe_subscription: stripe.Subscription,
):
    """
    Handle subscription.deleted event.

    This is fired when a subscription is canceled and reaches its end date.
    """
    logger.info(f"Processing subscription.deleted: {stripe_subscription.id}")

    # Find subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription.id
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        logger.warning(f"Subscription {stripe_subscription.id} not found in database")
        return

    # Update subscription status
    subscription.status = SubscriptionStatus.CANCELED
    subscription.ended_at = datetime.utcnow()

    # Deactivate tenant
    result = await db.execute(
        select(Tenant).where(Tenant.id == subscription.tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if tenant:
        tenant.is_active = False
        tenant.is_trial = False

    await db.commit()
    logger.info(f"Subscription {stripe_subscription.id} marked as canceled")


async def handle_trial_will_end(
    db: AsyncSession,
    stripe_subscription: stripe.Subscription,
):
    """
    Handle subscription.trial_will_end event.

    This is fired 3 days before trial ends. Use this to send reminder emails.
    """
    logger.info(
        f"Processing trial_will_end: {stripe_subscription.id} "
        f"(ends {stripe_subscription.trial_end})"
    )

    # Find subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription.id
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        logger.warning(f"Subscription {stripe_subscription.id} not found")
        return

    # TODO: Send trial ending reminder email
    # For now, just log it
    logger.info(
        f"Trial ending soon for tenant {subscription.tenant_id}. "
        "TODO: Send reminder email."
    )


async def handle_payment_succeeded(
    db: AsyncSession,
    invoice: stripe.Invoice,
):
    """
    Handle invoice.payment_succeeded event.

    This is fired when a payment succeeds (initial or renewal).
    """
    logger.info(
        f"Processing payment_succeeded: {invoice.id} "
        f"for subscription {invoice.subscription}"
    )

    if not invoice.subscription:
        logger.info("Invoice not associated with subscription, skipping")
        return

    # Find subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == invoice.subscription
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        logger.warning(f"Subscription {invoice.subscription} not found")
        return

    # Update subscription status
    subscription.status = SubscriptionStatus.ACTIVE

    # Activate tenant
    result = await db.execute(
        select(Tenant).where(Tenant.id == subscription.tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if tenant:
        tenant.is_active = True
        tenant.is_trial = False

    await db.commit()
    logger.info(f"Payment succeeded for subscription {invoice.subscription}")

    # TODO: Send payment receipt email


async def handle_payment_failed(
    db: AsyncSession,
    invoice: stripe.Invoice,
):
    """
    Handle invoice.payment_failed event.

    This is fired when a payment fails. Stripe will retry automatically,
    but we should notify the user and potentially restrict access.
    """
    logger.info(
        f"Processing payment_failed: {invoice.id} "
        f"for subscription {invoice.subscription}"
    )

    if not invoice.subscription:
        logger.info("Invoice not associated with subscription, skipping")
        return

    # Find subscription
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == invoice.subscription
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        logger.warning(f"Subscription {invoice.subscription} not found")
        return

    # Update subscription status
    subscription.status = SubscriptionStatus.PAST_DUE

    await db.commit()
    logger.warning(f"Payment failed for subscription {invoice.subscription}")

    # TODO: Send payment failed notification email
    # TODO: Consider restricting access after multiple failures

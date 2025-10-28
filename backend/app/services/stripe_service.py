"""
Stripe payment integration service for subscription management.

This service handles:
- Creating Stripe customers
- Creating checkout sessions
- Managing subscriptions
- Handling plan upgrades/downgrades
- Processing webhooks
"""

import stripe
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
import json

from ..core.config import settings
from ..models.subscription import Subscription, SubscriptionStatus, SubscriptionTier
from ..models.tenant import Tenant
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for managing Stripe subscriptions."""

    def __init__(self):
        """Initialize Stripe service with API key."""
        self.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_key = self.api_key

    @staticmethod
    def load_pricing_config() -> Dict[str, Any]:
        """Load pricing configuration from config/pricing.json."""
        import os
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "config", "pricing.json"
        )
        with open(config_path, "r") as f:
            return json.load(f)

    async def create_customer(
        self,
        email: str,
        name: str,
        tenant_id: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> stripe.Customer:
        """
        Create a Stripe customer.

        Args:
            email: Customer email
            name: Customer name (company name)
            tenant_id: Tenant UUID for reference
            metadata: Additional metadata

        Returns:
            Stripe Customer object
        """
        customer_metadata = {
            "tenant_id": tenant_id,
            **(metadata or {}),
        }

        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata=customer_metadata,
        )

        return customer

    async def create_checkout_session(
        self,
        customer_id: str,
        tier: SubscriptionTier,
        billing_cycle: str,
        success_url: str,
        cancel_url: str,
        trial_days: int = 14,
    ) -> stripe.checkout.Session:
        """
        Create a Stripe Checkout session for subscription.

        Args:
            customer_id: Stripe customer ID
            tier: Subscription tier (starter, professional, enterprise)
            billing_cycle: monthly or annual
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if user cancels
            trial_days: Number of trial days (default 14)

        Returns:
            Stripe Checkout Session object
        """
        pricing_config = self.load_pricing_config()
        plan = pricing_config["plans"][tier.value]
        price_id = plan["pricing"][billing_cycle]["stripe_price_id"]

        # Note: In production, you need to create these prices in Stripe Dashboard
        # or use the setup_stripe_products.py script

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            subscription_data={
                "trial_period_days": trial_days,
                "metadata": {
                    "tier": tier.value,
                    "billing_cycle": billing_cycle,
                },
            },
            allow_promotion_codes=True,
        )

        return session

    async def update_subscription_tier(
        self,
        subscription_id: str,
        new_tier: SubscriptionTier,
        billing_cycle: str,
        prorate: bool = True,
    ) -> stripe.Subscription:
        """
        Update subscription to new tier (upgrade/downgrade).

        Args:
            subscription_id: Stripe subscription ID
            new_tier: New subscription tier
            billing_cycle: monthly or annual
            prorate: Whether to prorate the charges

        Returns:
            Updated Stripe Subscription object
        """
        pricing_config = self.load_pricing_config()
        plan = pricing_config["plans"][new_tier.value]
        new_price_id = plan["pricing"][billing_cycle]["stripe_price_id"]

        # Get current subscription
        subscription = stripe.Subscription.retrieve(subscription_id)

        # Update subscription items
        stripe.Subscription.modify(
            subscription_id,
            items=[
                {
                    "id": subscription["items"]["data"][0]["id"],
                    "price": new_price_id,
                }
            ],
            proration_behavior="always_invoice" if prorate else "none",
            metadata={
                "tier": new_tier.value,
                "billing_cycle": billing_cycle,
            },
        )

        return stripe.Subscription.retrieve(subscription_id)

    async def cancel_subscription(
        self,
        subscription_id: str,
        cancel_at_period_end: bool = True,
    ) -> stripe.Subscription:
        """
        Cancel a subscription.

        Args:
            subscription_id: Stripe subscription ID
            cancel_at_period_end: If True, cancel at end of billing period.
                                  If False, cancel immediately.

        Returns:
            Updated Stripe Subscription object
        """
        if cancel_at_period_end:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True,
            )
        else:
            subscription = stripe.Subscription.delete(subscription_id)

        return subscription

    async def reactivate_subscription(
        self,
        subscription_id: str,
    ) -> stripe.Subscription:
        """
        Reactivate a canceled subscription (before period end).

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Updated Stripe Subscription object
        """
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=False,
        )

        return subscription

    async def sync_subscription_from_stripe(
        self,
        db: AsyncSession,
        stripe_subscription: stripe.Subscription,
    ) -> Subscription:
        """
        Sync subscription data from Stripe to database.

        Args:
            db: Database session
            stripe_subscription: Stripe Subscription object

        Returns:
            Updated Subscription model
        """
        # Find subscription by Stripe subscription ID
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription.id
            )
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            # Find by Stripe customer ID
            result = await db.execute(
                select(Subscription).where(
                    Subscription.stripe_customer_id == stripe_subscription.customer
                )
            )
            subscription = result.scalar_one_or_none()

        if not subscription:
            raise ValueError(
                f"Subscription not found for Stripe subscription {stripe_subscription.id}"
            )

        # Update subscription fields
        subscription.stripe_subscription_id = stripe_subscription.id
        subscription.status = SubscriptionStatus(stripe_subscription.status)
        subscription.current_period_start = datetime.fromtimestamp(
            stripe_subscription.current_period_start
        )
        subscription.current_period_end = datetime.fromtimestamp(
            stripe_subscription.current_period_end
        )

        # Update trial information
        if stripe_subscription.trial_start:
            subscription.trial_start = datetime.fromtimestamp(
                stripe_subscription.trial_start
            )
        if stripe_subscription.trial_end:
            subscription.trial_end = datetime.fromtimestamp(
                stripe_subscription.trial_end
            )

        # Update cancellation information
        if stripe_subscription.canceled_at:
            subscription.canceled_at = datetime.fromtimestamp(
                stripe_subscription.canceled_at
            )
        if stripe_subscription.ended_at:
            subscription.ended_at = datetime.fromtimestamp(
                stripe_subscription.ended_at
            )

        # Update amount
        if stripe_subscription.items.data:
            item = stripe_subscription.items.data[0]
            subscription.amount = Decimal(item.price.unit_amount) / 100
            subscription.currency = item.price.currency.upper()
            subscription.stripe_price_id = item.price.id

        # Update tier from metadata
        if "tier" in stripe_subscription.metadata:
            subscription.tier = SubscriptionTier(stripe_subscription.metadata["tier"])

        # Update billing cycle from metadata
        if "billing_cycle" in stripe_subscription.metadata:
            subscription.billing_cycle = stripe_subscription.metadata["billing_cycle"]

        await db.commit()
        await db.refresh(subscription)

        return subscription

    async def get_billing_history(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> List[stripe.Invoice]:
        """
        Get billing history for a customer.

        Args:
            customer_id: Stripe customer ID
            limit: Number of invoices to retrieve

        Returns:
            List of Stripe Invoice objects
        """
        invoices = stripe.Invoice.list(
            customer=customer_id,
            limit=limit,
        )

        return invoices.data

    async def create_customer_portal_session(
        self,
        customer_id: str,
        return_url: str,
    ) -> stripe.billing_portal.Session:
        """
        Create a Stripe Customer Portal session for managing subscription.

        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal session

        Returns:
            Stripe Customer Portal Session object
        """
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )

        return session

    @staticmethod
    def verify_webhook_signature(
        payload: bytes,
        signature: str,
        webhook_secret: str,
    ) -> stripe.Event:
        """
        Verify and construct Stripe webhook event.

        Args:
            payload: Raw request body
            signature: Stripe-Signature header value
            webhook_secret: Webhook signing secret from Stripe

        Returns:
            Constructed Stripe Event object

        Raises:
            ValueError: If signature verification fails
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return event
        except ValueError as e:
            raise ValueError(f"Invalid payload: {e}")
        except stripe.error.SignatureVerificationError as e:
            raise ValueError(f"Invalid signature: {e}")


# Singleton instance
stripe_service = StripeService()

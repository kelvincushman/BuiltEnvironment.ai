# Payment Integration Guide - Stripe & RevenueCat

## Overview

This document provides comprehensive guidance for integrating Stripe and RevenueCat payment systems into BuiltEnvironment.ai SaaS platform.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React)                             │
│  - Pricing page                                                 │
│  - Checkout flow                                                │
│  - Account/billing management                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                        │
│  - Subscription management                                      │
│  - Webhook handlers                                             │
│  - Usage tracking                                               │
└───────────┬──────────────────────┬──────────────────────────────┘
            │                      │
            ▼                      ▼
  ┌──────────────────┐   ┌──────────────────┐
  │     Stripe       │   │   RevenueCat     │
  │  - Payments      │   │  - Subscriptions │
  │  - Invoicing     │   │  - Cross-platform│
  │  - Tax           │   │  - Analytics     │
  └──────────────────┘   └──────────────────┘
```

---

## Why Both Stripe and RevenueCat?

### Stripe
- **Direct payment processing** for web customers
- **Invoicing** for enterprise customers
- **Tax calculation** and compliance
- **Full control** over payment flows
- **Lower fees** (2.9% + 30p vs RevenueCat's additional fee)

### RevenueCat
- **Cross-platform subscription management** (if we build mobile apps)
- **Unified analytics** across iOS, Android, and Web
- **Server-side receipt validation**
- **Simplified webhook management**
- **Built-in experiments** and pricing tests

### Recommended Architecture
- **Web-only initially**: Use Stripe directly
- **Future mobile apps**: Add RevenueCat as subscription abstraction layer
- **Enterprise**: Direct Stripe invoicing with custom billing

---

## Implementation Phase 1: Stripe Direct Integration

### 1.1 Stripe Setup

**Installation**:
```bash
pip install stripe
npm install @stripe/stripe-js @stripe/react-stripe-js
```

**Environment Variables**:
```bash
# .env
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 1.2 Create Stripe Products and Prices

**Python Script** (`scripts/setup_stripe_products.py`):
```python
import stripe
import json

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Load pricing config
with open("config/pricing.json") as f:
    pricing_config = json.load(f)

def create_stripe_products():
    """Create Stripe products and prices from pricing.json"""

    products = {}

    for plan_id, plan_data in pricing_config["plans"].items():
        # Create product
        product = stripe.Product.create(
            name=plan_data["name"],
            description=plan_data["description"],
            metadata={
                "plan_id": plan_id,
                "target_audience": plan_data["target_audience"]
            }
        )

        products[plan_id] = product.id

        # Create monthly price
        monthly_price = stripe.Price.create(
            product=product.id,
            unit_amount=int(plan_data["pricing"]["monthly"]["amount"] * 100),  # Convert to pence
            currency="gbp",
            recurring={"interval": "month"},
            metadata={"plan_id": plan_id, "period": "monthly"}
        )

        # Create annual price
        annual_price = stripe.Price.create(
            product=product.id,
            unit_amount=int(plan_data["pricing"]["annual"]["amount"] * 100),
            currency="gbp",
            recurring={"interval": "year"},
            metadata={"plan_id": plan_id, "period": "annual"}
        )

        print(f"Created {plan_data['name']}")
        print(f"  Monthly Price ID: {monthly_price.id}")
        print(f"  Annual Price ID: {annual_price.id}")

        # Update pricing.json with actual Stripe IDs
        pricing_config["plans"][plan_id]["pricing"]["monthly"]["stripe_price_id"] = monthly_price.id
        pricing_config["plans"][plan_id]["pricing"]["annual"]["stripe_price_id"] = annual_price.id

    # Save updated pricing config
    with open("config/pricing.json", "w") as f:
        json.dump(pricing_config, f, indent=2)

    return products


def create_addon_prices():
    """Create prices for add-ons"""

    # Additional users
    for plan_id in ["starter", "professional"]:
        price = stripe.Price.create(
            unit_amount=int(pricing_config["add_ons"]["additional_users"]["pricing"][plan_id]["amount"] * 100),
            currency="gbp",
            recurring={"interval": "month"},
            product_data={
                "name": f"Additional Users - {plan_id.title()}",
                "metadata": {"addon": "users", "plan": plan_id}
            }
        )

        print(f"Created additional users price for {plan_id}: {price.id}")

    # Additional storage
    storage_price = stripe.Price.create(
        unit_amount=5000,  # £50 per 100GB
        currency="gbp",
        recurring={"interval": "month"},
        product_data={
            "name": "Additional Storage (100GB)",
            "metadata": {"addon": "storage"}
        }
    )

    print(f"Created storage price: {storage_price.id}")

    # Additional AI checks
    checks_price = stripe.Price.create(
        unit_amount=9900,  # £99 per 100 checks
        currency="gbp",
        product_data={
            "name": "Additional AI Checks (100)",
            "metadata": {"addon": "ai_checks"}
        }
    )

    print(f"Created AI checks price: {checks_price.id}")


if __name__ == "__main__":
    create_stripe_products()
    create_addon_prices()
```

### 1.3 Backend: Subscription Management API

**Subscription Models** (`models/subscription.py`):
```python
from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

class SubscriptionStatus(str, enum.Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    PAUSED = "paused"

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Stripe IDs
    stripe_customer_id = Column(String, unique=True, index=True)
    stripe_subscription_id = Column(String, unique=True, index=True)
    stripe_price_id = Column(String)

    # Plan details
    plan_id = Column(String)  # starter, professional, enterprise
    billing_period = Column(String)  # monthly, annual

    # Status
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    trial_ends_at = Column(DateTime, nullable=True)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime, nullable=True)

    # Features and usage
    features = Column(JSON)  # Store plan features for quick access
    usage_current_period = Column(JSON, default={})  # Track usage

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Usage tracking
    metric = Column(String)  # documents_uploaded, ai_checks_run, storage_used_gb
    quantity = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Metadata
    metadata = Column(JSON, default={})
```

**Subscription API** (`api/subscription.py`):
```python
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
import stripe
from typing import Optional

router = APIRouter(prefix="/api/subscription", tags=["subscription"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class CheckoutRequest(BaseModel):
    plan_id: str
    billing_period: str  # monthly or annual
    success_url: str
    cancel_url: str


class SubscriptionResponse(BaseModel):
    id: str
    plan_id: str
    status: str
    current_period_end: datetime
    cancel_at_period_end: bool


@router.post("/checkout-session")
async def create_checkout_session(
    request: CheckoutRequest,
    current_user = Depends(get_current_user)
):
    """Create Stripe Checkout session for new subscription"""

    # Load pricing config
    with open("config/pricing.json") as f:
        pricing = json.load(f)

    plan = pricing["plans"].get(request.plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan")

    # Get price ID
    price_id = plan["pricing"][request.billing_period]["stripe_price_id"]

    # Get or create Stripe customer
    tenant = await get_tenant(current_user.tenant_id)

    if not tenant.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=tenant.name,
            metadata={
                "tenant_id": str(tenant.id),
                "user_id": str(current_user.id)
            }
        )
        tenant.stripe_customer_id = customer.id
        await db.commit()

    # Create checkout session
    session = stripe.checkout.Session.create(
        customer=tenant.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{
            "price": price_id,
            "quantity": 1
        }],
        mode="subscription",
        success_url=request.success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.cancel_url,
        subscription_data={
            "trial_period_days": pricing.get("trial_period_days", 14),
            "metadata": {
                "tenant_id": str(tenant.id),
                "plan_id": request.plan_id
            }
        },
        metadata={
            "tenant_id": str(tenant.id),
            "plan_id": request.plan_id
        }
    )

    return {"checkout_url": session.url, "session_id": session.id}


@router.get("/current")
async def get_current_subscription(
    current_user = Depends(get_current_user)
) -> SubscriptionResponse:
    """Get current user's subscription"""

    subscription = await db.query(Subscription).filter(
        Subscription.tenant_id == current_user.tenant_id
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")

    return SubscriptionResponse(
        id=str(subscription.id),
        plan_id=subscription.plan_id,
        status=subscription.status,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end
    )


@router.post("/cancel")
async def cancel_subscription(
    current_user = Depends(get_current_user)
):
    """Cancel subscription at end of current period"""

    subscription = await get_subscription(current_user.tenant_id)

    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")

    # Cancel in Stripe
    stripe.Subscription.modify(
        subscription.stripe_subscription_id,
        cancel_at_period_end=True
    )

    # Update local record
    subscription.cancel_at_period_end = True
    await db.commit()

    return {"message": "Subscription will cancel at end of current period"}


@router.post("/reactivate")
async def reactivate_subscription(
    current_user = Depends(get_current_user)
):
    """Reactivate a canceled subscription"""

    subscription = await get_subscription(current_user.tenant_id)

    if not subscription or not subscription.cancel_at_period_end:
        raise HTTPException(status_code=400, detail="Subscription not set to cancel")

    # Reactivate in Stripe
    stripe.Subscription.modify(
        subscription.stripe_subscription_id,
        cancel_at_period_end=False
    )

    # Update local record
    subscription.cancel_at_period_end = False
    await db.commit()

    return {"message": "Subscription reactivated"}


@router.post("/upgrade")
async def upgrade_subscription(
    new_plan_id: str,
    billing_period: str,
    current_user = Depends(get_current_user)
):
    """Upgrade/downgrade subscription plan"""

    subscription = await get_subscription(current_user.tenant_id)

    # Load pricing
    with open("config/pricing.json") as f:
        pricing = json.load(f)

    new_price_id = pricing["plans"][new_plan_id]["pricing"][billing_period]["stripe_price_id"]

    # Update Stripe subscription
    stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)

    stripe.Subscription.modify(
        subscription.stripe_subscription_id,
        items=[{
            "id": stripe_sub["items"]["data"][0].id,
            "price": new_price_id
        }],
        proration_behavior="always_invoice"  # Charge/credit immediately
    )

    # Update local record
    subscription.plan_id = new_plan_id
    subscription.billing_period = billing_period
    subscription.stripe_price_id = new_price_id
    subscription.features = pricing["plans"][new_plan_id]["features"]
    await db.commit()

    return {"message": f"Subscription upgraded to {new_plan_id}"}


@router.get("/customer-portal")
async def get_customer_portal_url(
    current_user = Depends(get_current_user)
):
    """Get Stripe customer portal URL for managing subscription"""

    tenant = await get_tenant(current_user.tenant_id)

    if not tenant.stripe_customer_id:
        raise HTTPException(status_code=404, detail="No Stripe customer found")

    # Create portal session
    session = stripe.billing_portal.Session.create(
        customer=tenant.stripe_customer_id,
        return_url=f"{os.getenv('FRONTEND_URL')}/account/billing"
    )

    return {"portal_url": session.url}
```

### 1.4 Webhook Handler

**Webhook Endpoint** (`api/webhooks/stripe.py`):
```python
from fastapi import APIRouter, Request, HTTPException
import stripe
from stripe.error import SignatureVerificationError

router = APIRouter(prefix="/webhooks/stripe", tags=["webhooks"])

@router.post("")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle different event types
    if event["type"] == "checkout.session.completed":
        await handle_checkout_completed(event["data"]["object"])

    elif event["type"] == "customer.subscription.created":
        await handle_subscription_created(event["data"]["object"])

    elif event["type"] == "customer.subscription.updated":
        await handle_subscription_updated(event["data"]["object"])

    elif event["type"] == "customer.subscription.deleted":
        await handle_subscription_deleted(event["data"]["object"])

    elif event["type"] == "invoice.payment_succeeded":
        await handle_payment_succeeded(event["data"]["object"])

    elif event["type"] == "invoice.payment_failed":
        await handle_payment_failed(event["data"]["object"])

    return {"status": "success"}


async def handle_checkout_completed(session):
    """Handle successful checkout"""

    tenant_id = session["metadata"]["tenant_id"]
    plan_id = session["metadata"]["plan_id"]

    # Retrieve subscription details
    subscription_id = session["subscription"]
    stripe_sub = stripe.Subscription.retrieve(subscription_id)

    # Load plan features
    with open("config/pricing.json") as f:
        pricing = json.load(f)

    features = pricing["plans"][plan_id]["features"]

    # Create subscription record
    subscription = Subscription(
        tenant_id=tenant_id,
        stripe_customer_id=session["customer"],
        stripe_subscription_id=subscription_id,
        stripe_price_id=stripe_sub["items"]["data"][0]["price"]["id"],
        plan_id=plan_id,
        billing_period="monthly" if stripe_sub["items"]["data"][0]["price"]["recurring"]["interval"] == "month" else "annual",
        status=SubscriptionStatus.TRIAL if stripe_sub["status"] == "trialing" else SubscriptionStatus.ACTIVE,
        trial_ends_at=datetime.fromtimestamp(stripe_sub["trial_end"]) if stripe_sub.get("trial_end") else None,
        current_period_start=datetime.fromtimestamp(stripe_sub["current_period_start"]),
        current_period_end=datetime.fromtimestamp(stripe_sub["current_period_end"]),
        features=features
    )

    await db.add(subscription)
    await db.commit()

    # Send welcome email
    await send_welcome_email(tenant_id)

    # Log audit event
    await audit_logger.log_event({
        "event_type": "subscription.created",
        "actor": {"type": "system", "id": "stripe"},
        "target": {"type": "subscription", "id": str(subscription.id)},
        "context": {"tenant_id": tenant_id},
        "data": {"plan_id": plan_id, "billing_period": subscription.billing_period}
    })


async def handle_subscription_updated(stripe_sub):
    """Handle subscription updates"""

    subscription = await db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_sub["id"]
    ).first()

    if not subscription:
        return

    # Update subscription
    subscription.status = map_stripe_status(stripe_sub["status"])
    subscription.current_period_start = datetime.fromtimestamp(stripe_sub["current_period_start"])
    subscription.current_period_end = datetime.fromtimestamp(stripe_sub["current_period_end"])
    subscription.cancel_at_period_end = stripe_sub["cancel_at_period_end"]

    if stripe_sub.get("canceled_at"):
        subscription.canceled_at = datetime.fromtimestamp(stripe_sub["canceled_at"])

    await db.commit()


async def handle_payment_succeeded(invoice):
    """Handle successful payment"""

    subscription = await db.query(Subscription).filter(
        Subscription.stripe_subscription_id == invoice["subscription"]
    ).first()

    if not subscription:
        return

    # Reset usage for new billing period
    subscription.usage_current_period = {}
    await db.commit()

    # Send payment receipt
    await send_payment_receipt(subscription.tenant_id, invoice)


async def handle_payment_failed(invoice):
    """Handle failed payment"""

    subscription = await db.query(Subscription).filter(
        Subscription.stripe_subscription_id == invoice["subscription"]
    ).first()

    if not subscription:
        return

    subscription.status = SubscriptionStatus.PAST_DUE
    await db.commit()

    # Send payment failure notification
    await send_payment_failure_notification(subscription.tenant_id)


def map_stripe_status(stripe_status: str) -> SubscriptionStatus:
    """Map Stripe status to our status enum"""
    mapping = {
        "trialing": SubscriptionStatus.TRIAL,
        "active": SubscriptionStatus.ACTIVE,
        "past_due": SubscriptionStatus.PAST_DUE,
        "canceled": SubscriptionStatus.CANCELED,
        "paused": SubscriptionStatus.PAUSED
    }
    return mapping.get(stripe_status, SubscriptionStatus.ACTIVE)
```

### 1.5 Usage Tracking and Limits

**Usage Tracking** (`services/usage_tracker.py`):
```python
from typing import Dict
from datetime import datetime

class UsageTracker:
    """Track usage against subscription limits"""

    def __init__(self, db_session):
        self.db = db_session

    async def track_usage(
        self,
        tenant_id: str,
        metric: str,
        quantity: int = 1,
        metadata: Dict = None
    ):
        """Record usage event"""

        subscription = await self.get_subscription(tenant_id)

        # Record in usage_records table
        record = UsageRecord(
            tenant_id=tenant_id,
            subscription_id=subscription.id,
            metric=metric,
            quantity=quantity,
            metadata=metadata or {}
        )

        await self.db.add(record)

        # Update current period usage
        current_usage = subscription.usage_current_period.copy()
        current_usage[metric] = current_usage.get(metric, 0) + quantity
        subscription.usage_current_period = current_usage

        await self.db.commit()

    async def check_limit(
        self,
        tenant_id: str,
        metric: str
    ) -> tuple[bool, int, int]:
        """Check if tenant has exceeded limit

        Returns:
            (within_limit, current_usage, limit)
        """

        subscription = await self.get_subscription(tenant_id)

        # Get current usage
        current_usage = subscription.usage_current_period.get(metric, 0)

        # Get limit from features
        limit = subscription.features.get(f"{metric}_per_month")

        if limit == "unlimited":
            return True, current_usage, float('inf')

        if limit is None:
            # No limit defined, allow
            return True, current_usage, float('inf')

        within_limit = current_usage < limit

        return within_limit, current_usage, limit

    async def enforce_limit(
        self,
        tenant_id: str,
        metric: str,
        action_name: str = "action"
    ):
        """Enforce usage limit, raise exception if exceeded"""

        within_limit, current, limit = await self.check_limit(tenant_id, metric)

        if not within_limit:
            raise UsageLimitExceeded(
                f"Usage limit exceeded for {metric}. Current: {current}, Limit: {limit}. "
                f"Please upgrade your plan or purchase additional {metric}."
            )


class UsageLimitExceeded(Exception):
    """Exception raised when usage limit is exceeded"""
    pass


# Usage in API endpoints
@router.post("/documents/upload")
async def upload_document(
    file: UploadFile,
    current_user = Depends(get_current_user)
):
    """Upload document with usage tracking"""

    usage_tracker = UsageTracker(db)

    # Check limit before processing
    await usage_tracker.enforce_limit(
        current_user.tenant_id,
        "documents",
        "document upload"
    )

    # Process upload
    document = await process_document_upload(file, current_user)

    # Track usage
    await usage_tracker.track_usage(
        current_user.tenant_id,
        "documents",
        quantity=1,
        metadata={"document_id": str(document.id), "filename": file.filename}
    )

    return {"document_id": str(document.id)}
```

---

## Frontend Integration

### React Pricing Page

**Pricing Component** (`components/Pricing.tsx`):
```typescript
import React from 'react';
import { loadStripe } from '@stripe/stripe-js';
import pricingData from '../../config/pricing.json';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY!);

export const PricingPage: React.FC = () => {
  const [billingPeriod, setBillingPeriod] = React.useState<'monthly' | 'annual'>('annual');

  const handleCheckout = async (planId: string) => {
    const response = await fetch('/api/subscription/checkout-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`
      },
      body: JSON.stringify({
        plan_id: planId,
        billing_period: billingPeriod,
        success_url: `${window.location.origin}/account/billing?success=true`,
        cancel_url: `${window.location.origin}/pricing`
      })
    });

    const { checkout_url } = await response.json();
    window.location.href = checkout_url;
  };

  return (
    <div className="pricing-page">
      <h1>Choose Your Plan</h1>

      <div className="billing-toggle">
        <button onClick={() => setBillingPeriod('monthly')}>Monthly</button>
        <button onClick={() => setBillingPeriod('annual')}>
          Annual <span className="save-badge">Save 17%</span>
        </button>
      </div>

      <div className="pricing-cards">
        {Object.entries(pricingData.plans).map(([id, plan]) => (
          <PricingCard
            key={id}
            planId={id}
            plan={plan}
            billingPeriod={billingPeriod}
            onCheckout={handleCheckout}
          />
        ))}
      </div>
    </div>
  );
};
```

---

## Implementation Phase 2: RevenueCat (Future Mobile)

When building mobile apps, add RevenueCat as abstraction layer:

```python
# Install
pip install revenuecat

# Configure
import revenuecat
revenuecat.configure(api_key=os.getenv("REVENUECAT_API_KEY"))

# Sync with Stripe
# RevenueCat will handle subscription state across platforms
```

---

## Testing

### Test Mode Setup

```bash
# Use Stripe test keys
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# Test card numbers
# Success: 4242 4242 4242 4242
# Declined: 4000 0000 0000 0002
# 3D Secure: 4000 0025 0000 3155
```

### Webhook Testing

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Forward webhooks to local
stripe listen --forward-to localhost:8000/webhooks/stripe
```

---

## Security Best Practices

1. **Never expose secret keys** in frontend code
2. **Validate webhooks** using Stripe signatures
3. **Idempotent webhook handlers** (handle duplicates gracefully)
4. **Store prices in Stripe** as source of truth
5. **Use HTTPS** for all API calls
6. **Implement rate limiting** on checkout endpoints
7. **Log all subscription changes** in audit system

---

## Go-Live Checklist

- [ ] Switch to live Stripe keys
- [ ] Configure production webhook endpoint
- [ ] Set up Stripe billing portal
- [ ] Configure tax calculation (Stripe Tax)
- [ ] Set up invoice emails
- [ ] Test full checkout flow
- [ ] Test subscription upgrade/downgrade
- [ ] Test cancellation flow
- [ ] Monitor webhook delivery
- [ ] Set up Stripe dashboard alerts

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-27

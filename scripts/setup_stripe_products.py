#!/usr/bin/env python3
"""
Setup Stripe products and prices from config/pricing.json

This script creates all products and prices in your Stripe account based on
the pricing configuration. Run this once when setting up your Stripe account.

Usage:
    python scripts/setup_stripe_products.py

Requirements:
    - STRIPE_SECRET_KEY environment variable must be set
    - Stripe Python library must be installed
"""

import json
import os
import sys
import stripe
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.config import settings


def load_pricing_config():
    """Load pricing configuration from config/pricing.json"""
    config_path = Path(__file__).parent.parent / "config" / "pricing.json"
    with open(config_path, "r") as f:
        return json.load(f)


def create_product(name: str, description: str, metadata: dict) -> stripe.Product:
    """Create a Stripe product"""
    print(f"\n📦 Creating product: {name}")

    product = stripe.Product.create(
        name=name,
        description=description,
        metadata=metadata,
    )

    print(f"   ✅ Created product: {product.id}")
    return product


def create_price(
    product_id: str,
    amount: int,
    currency: str,
    interval: str,
    metadata: dict,
) -> stripe.Price:
    """Create a Stripe price for a product"""
    recurring = {"interval": interval}

    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount,
        currency=currency,
        recurring=recurring,
        metadata=metadata,
    )

    print(f"   💰 Created {interval} price: {price.id} (£{amount/100:.2f})")
    return price


def setup_stripe_products():
    """
    Setup all Stripe products and prices from pricing.json
    """
    # Initialize Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if not stripe.api_key or stripe.api_key == "":
        print("❌ Error: STRIPE_SECRET_KEY not set in environment")
        print("   Set it with: export STRIPE_SECRET_KEY=sk_test_...")
        sys.exit(1)

    print("🚀 Setting up Stripe products and prices...")
    print(f"   Using Stripe key: {stripe.api_key[:12]}...")

    # Load pricing config
    config = load_pricing_config()
    currency = config["currency"].lower()

    # Create products and prices for each plan
    plans = config["plans"]
    price_ids = {}

    for plan_id, plan_data in plans.items():
        print(f"\n{'='*60}")
        print(f"Setting up: {plan_data['name']} Plan")
        print(f"{'='*60}")

        # Create product
        product = create_product(
            name=f"{plan_data['name']} Plan",
            description=plan_data['description'],
            metadata={
                "plan_id": plan_id,
                "users": str(plan_data['features']['users']),
                "projects": str(plan_data['features']['projects']),
                "storage_gb": str(plan_data['features']['storage_gb']),
            }
        )

        # Create monthly price
        monthly_amount = int(plan_data['pricing']['monthly']['amount'] * 100)  # Convert to cents
        monthly_price = create_price(
            product_id=product.id,
            amount=monthly_amount,
            currency=currency,
            interval="month",
            metadata={
                "plan_id": plan_id,
                "billing_cycle": "monthly",
            }
        )

        price_ids[f"{plan_id}_monthly"] = monthly_price.id

        # Create annual price
        annual_amount = int(plan_data['pricing']['annual']['amount'] * 100)  # Convert to cents
        annual_price = create_price(
            product_id=product.id,
            amount=annual_amount,
            currency=currency,
            interval="year",
            metadata={
                "plan_id": plan_id,
                "billing_cycle": "annual",
            }
        )

        price_ids[f"{plan_id}_annual"] = annual_price.id

    # Print summary
    print(f"\n{'='*60}")
    print("✅ Setup Complete!")
    print(f"{'='*60}")
    print("\n📝 Price IDs created:")
    print("\nAdd these to your .env file:\n")

    for key, price_id in price_ids.items():
        print(f"STRIPE_PRICE_{key.upper()}={price_id}")

    print("\n⚠️  IMPORTANT: Update config/pricing.json with these price IDs")
    print("   Replace the placeholder IDs with the real ones above.")

    print("\n📖 Next steps:")
    print("   1. Update config/pricing.json with the price IDs above")
    print("   2. Configure Stripe webhook endpoint:")
    print("      URL: https://your-domain.com/api/v1/webhooks/stripe")
    print("      Events: customer.subscription.*, invoice.*")
    print("   3. Add STRIPE_WEBHOOK_SECRET to your .env file")
    print("   4. Test the checkout flow in your application")

    return price_ids


def main():
    """Main entry point"""
    try:
        price_ids = setup_stripe_products()

        # Optionally save price IDs to a file
        output_file = Path(__file__).parent.parent / "config" / "stripe_price_ids.json"
        with open(output_file, "w") as f:
            json.dump(price_ids, f, indent=2)

        print(f"\n💾 Price IDs saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

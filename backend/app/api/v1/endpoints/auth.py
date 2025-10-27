"""
Authentication endpoints for user registration, login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import re

from ....db.base import get_db
from ....models.user import User
from ....models.tenant import Tenant
from ....models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from ....schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    Token,
)
from ....core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter()


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from company name."""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    return slug.strip('-')


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user and create their tenant (organization).

    This creates:
    - A new tenant (organization)
    - The first user (admin)
    - A trial subscription

    Returns JWT tokens for immediate authentication.
    """

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Generate unique slug for tenant
    base_slug = generate_slug(request.company_name)
    slug = base_slug
    counter = 1

    while True:
        result = await db.execute(select(Tenant).where(Tenant.slug == slug))
        if not result.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Create tenant
    tenant = Tenant(
        name=request.company_name,
        slug=slug,
        email=request.company_email,
        is_active=True,
        is_trial=True,
    )
    db.add(tenant)
    await db.flush()  # Get tenant.id

    # Create subscription (trial)
    subscription = Subscription(
        tenant_id=tenant.id,
        tier=SubscriptionTier.STARTER,
        status=SubscriptionStatus.TRIALING,
        amount=0.00,
        currency="GBP",
    )
    db.add(subscription)

    # Create user (admin)
    user = User(
        tenant_id=tenant.id,
        email=request.email,
        hashed_password=get_password_hash(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        phone=request.phone,
        is_active=True,
        is_verified=True,  # Auto-verify for MVP (add email verification later)
        role="admin",
        last_login_at=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()

    # Generate tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "tenant_id": str(tenant.id),
        "role": user.role,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT tokens.
    """

    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # Generate tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "tenant_id": str(user.tenant_id),
        "role": user.role,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    """

    # Decode refresh token
    payload = decode_token(request.refresh_token)

    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # Create new tokens
    token_data = {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "tenant_id": payload.get("tenant_id"),
        "role": payload.get("role"),
    }

    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )

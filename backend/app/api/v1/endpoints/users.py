"""
User profile management endpoints.

Provides endpoints for users to manage their own profiles.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from ....db.base import get_db
from ....models.user import User
from ....schemas.user import User as UserSchema, UserUpdate, ChangePasswordRequest
from ....schemas.auth import MessageResponse
from ....core.security import verify_password, get_password_hash
from ....core.deps import get_current_user
from ....services.audit_logger import audit_logger
from ....models.audit import EventType

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's profile.

    Returns complete profile information for the authenticated user.
    """
    # Refresh user data from database to ensure up-to-date info
    result = await db.execute(
        select(User).where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.patch("/me", response_model=UserSchema)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's profile.

    Allows users to update their own profile information:
    - First name
    - Last name
    - Phone number
    - Job title

    Email and role cannot be changed via this endpoint.
    """
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    # Log audit event
    await audit_logger.log_user_action(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="update_profile",
        event_type=EventType.USER_AUTH,
        status="success",
        description=f"User '{user.email}' updated profile",
        metadata={"updated_fields": list(update_data.keys())},
    )

    return user


@router.post("/me/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change current user's password.

    Requires:
    - Current password (for verification)
    - New password (min 8 characters)

    Security:
    - Verifies current password before allowing change
    - Logs password change event
    """
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Verify current password
    if not verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Check new password is different
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    # Update password
    user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()

    # Log audit event
    await audit_logger.log_user_action(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="change_password",
        event_type=EventType.USER_AUTH,
        status="success",
        description=f"User '{user.email}' changed password",
    )

    return MessageResponse(message="Password changed successfully")


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user by ID.

    Only users within the same tenant can view each other's profiles.
    Enforces tenant isolation.
    """
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id,  # Tenant isolation
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.get("/", response_model=list[UserSchema])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    List all users in current tenant.

    Pagination:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 100)

    Returns users in the same tenant as the current user.
    """
    # Enforce max limit
    limit = min(limit, 100)

    result = await db.execute(
        select(User)
        .where(User.tenant_id == current_user.tenant_id)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    return users

"""
Usage tracking service for monitoring and enforcing subscription limits.

This service tracks:
- Projects created
- Documents uploaded
- Storage used
- Users in tenant
- AI compliance checks run

It also enforces limits based on subscription tier.
"""

from typing import Dict, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
import json
from pathlib import Path

from ..models.tenant import Tenant
from ..models.subscription import Subscription, SubscriptionTier
from ..models.project import Project
from ..models.document import Document
from ..models.user import User
from ..schemas.subscription import UsageStats


class UsageTracker:
    """Service for tracking and enforcing usage limits."""

    @staticmethod
    def load_pricing_config() -> Dict:
        """Load pricing configuration to get limits"""
        config_path = Path(__file__).parent.parent.parent / "config" / "pricing.json"
        with open(config_path, "r") as f:
            return json.load(f)

    async def get_usage_stats(
        self,
        tenant_id: UUID,
        db: AsyncSession,
    ) -> UsageStats:
        """
        Get current usage statistics for a tenant.

        Args:
            tenant_id: Tenant UUID
            db: Database session

        Returns:
            UsageStats object with current usage and limits
        """
        # Get tenant and subscription
        result = await db.execute(
            select(Tenant, Subscription)
            .join(Subscription, Tenant.id == Subscription.tenant_id)
            .where(Tenant.id == tenant_id)
        )
        row = result.one_or_none()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant or subscription not found",
            )

        tenant, subscription = row

        # Load pricing config to get limits
        config = self.load_pricing_config()
        plan_features = config["plans"][subscription.tier.value]["features"]

        # Count projects
        result = await db.execute(
            select(func.count(Project.id)).where(Project.tenant_id == tenant_id)
        )
        projects_count = result.scalar() or 0

        # Count documents
        result = await db.execute(
            select(func.count(Document.id)).where(Document.tenant_id == tenant_id)
        )
        documents_count = result.scalar() or 0

        # Calculate storage used (sum of all document file sizes)
        result = await db.execute(
            select(func.sum(Document.file_size)).where(Document.tenant_id == tenant_id)
        )
        storage_bytes = result.scalar() or 0
        storage_gb = storage_bytes / (1024 ** 3)  # Convert bytes to GB

        # Count users
        result = await db.execute(
            select(func.count(User.id)).where(User.tenant_id == tenant_id)
        )
        users_count = result.scalar() or 0

        # Get AI checks count from subscription usage_data
        usage_data = subscription.usage_data or {}
        ai_checks_this_month = usage_data.get("ai_checks_this_month", 0)

        # Get limits from plan features
        projects_limit = tenant.max_projects
        users_limit = tenant.max_users
        storage_limit_gb = tenant.max_storage_gb

        # AI checks limit
        ai_checks_limit = plan_features.get("ai_checks_per_month")
        if ai_checks_limit == "unlimited":
            ai_checks_limit = None
        else:
            ai_checks_limit = int(ai_checks_limit)

        # Documents limit
        documents_limit = plan_features.get("documents_per_month")
        if documents_limit == "unlimited":
            documents_limit = None
        else:
            documents_limit = int(documents_limit)

        return UsageStats(
            projects_count=projects_count,
            projects_limit=projects_limit,
            documents_count=documents_count,
            documents_limit=documents_limit or 999999,  # Large number if unlimited
            storage_used_gb=storage_gb,
            storage_limit_gb=storage_limit_gb,
            users_count=users_count,
            users_limit=users_limit,
            ai_checks_this_month=ai_checks_this_month,
            ai_checks_limit=ai_checks_limit,
        )

    async def check_project_limit(
        self,
        tenant_id: UUID,
        db: AsyncSession,
    ) -> bool:
        """
        Check if tenant can create another project.

        Args:
            tenant_id: Tenant UUID
            db: Database session

        Returns:
            True if within limit

        Raises:
            HTTPException: If limit exceeded
        """
        stats = await self.get_usage_stats(tenant_id, db)

        if stats.projects_count >= stats.projects_limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Project limit reached ({stats.projects_limit}). Please upgrade your plan.",
            )

        return True

    async def check_document_limit(
        self,
        tenant_id: UUID,
        db: AsyncSession,
    ) -> bool:
        """
        Check if tenant can upload another document.

        Args:
            tenant_id: Tenant UUID
            db: Database session

        Returns:
            True if within limit

        Raises:
            HTTPException: If limit exceeded
        """
        stats = await self.get_usage_stats(tenant_id, db)

        if stats.documents_limit and stats.documents_count >= stats.documents_limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Monthly document limit reached ({stats.documents_limit}). Please upgrade your plan.",
            )

        return True

    async def check_storage_limit(
        self,
        tenant_id: UUID,
        file_size_bytes: int,
        db: AsyncSession,
    ) -> bool:
        """
        Check if tenant has enough storage for a new file.

        Args:
            tenant_id: Tenant UUID
            file_size_bytes: Size of file to upload
            db: Database session

        Returns:
            True if within limit

        Raises:
            HTTPException: If limit exceeded
        """
        stats = await self.get_usage_stats(tenant_id, db)

        file_size_gb = file_size_bytes / (1024 ** 3)
        new_total = stats.storage_used_gb + file_size_gb

        if new_total > stats.storage_limit_gb:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Storage limit exceeded ({stats.storage_limit_gb} GB). Please upgrade your plan.",
            )

        return True

    async def check_user_limit(
        self,
        tenant_id: UUID,
        db: AsyncSession,
    ) -> bool:
        """
        Check if tenant can add another user.

        Args:
            tenant_id: Tenant UUID
            db: Database session

        Returns:
            True if within limit

        Raises:
            HTTPException: If limit exceeded
        """
        stats = await self.get_usage_stats(tenant_id, db)

        if stats.users_count >= stats.users_limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"User limit reached ({stats.users_limit}). Please upgrade your plan.",
            )

        return True

    async def check_ai_check_limit(
        self,
        tenant_id: UUID,
        db: AsyncSession,
    ) -> bool:
        """
        Check if tenant can run another AI compliance check.

        Args:
            tenant_id: Tenant UUID
            db: Database session

        Returns:
            True if within limit

        Raises:
            HTTPException: If limit exceeded
        """
        stats = await self.get_usage_stats(tenant_id, db)

        # Unlimited checks
        if stats.ai_checks_limit is None:
            return True

        if stats.ai_checks_this_month >= stats.ai_checks_limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Monthly AI check limit reached ({stats.ai_checks_limit}). Please upgrade your plan.",
            )

        return True

    async def increment_ai_check_count(
        self,
        tenant_id: UUID,
        db: AsyncSession,
    ) -> None:
        """
        Increment AI check count for current month.

        Args:
            tenant_id: Tenant UUID
            db: Database session
        """
        result = await db.execute(
            select(Subscription).where(Subscription.tenant_id == tenant_id)
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            return

        # Get current usage data
        usage_data = subscription.usage_data or {}

        # Increment AI check count
        current_count = usage_data.get("ai_checks_this_month", 0)
        usage_data["ai_checks_this_month"] = current_count + 1

        # Update subscription
        subscription.usage_data = usage_data
        await db.commit()

    async def reset_monthly_usage(
        self,
        tenant_id: UUID,
        db: AsyncSession,
    ) -> None:
        """
        Reset monthly usage counters (called at billing cycle renewal).

        Args:
            tenant_id: Tenant UUID
            db: Database session
        """
        result = await db.execute(
            select(Subscription).where(Subscription.tenant_id == tenant_id)
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            return

        # Reset monthly counters
        usage_data = subscription.usage_data or {}
        usage_data["ai_checks_this_month"] = 0
        usage_data["documents_this_month"] = 0

        subscription.usage_data = usage_data
        await db.commit()


# Singleton instance
usage_tracker = UsageTracker()

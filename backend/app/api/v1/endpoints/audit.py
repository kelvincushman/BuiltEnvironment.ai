"""
Audit endpoints for querying activity logs.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from ....db.base import get_db
from ....models.audit import AuditEvent, EventType
from ....schemas.audit import (
    AuditEvent as AuditEventSchema,
    AuditEventList,
    AuditStatistics,
)
from ....core.security import CurrentUser

router = APIRouter()


@router.get("/", response_model=AuditEventList)
async def get_audit_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    event_type: Optional[EventType] = None,
    actor_type: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get audit events for current tenant with filtering and pagination.

    Filters:
    - event_type: Filter by event type (user.auth, ai.agent, etc.)
    - actor_type: Filter by actor type (user, ai_agent, system)
    - resource_id: Filter by specific resource
    - start_date: Filter events after this date
    - end_date: Filter events before this date

    Returns paginated list of audit events.
    """
    tenant_id = UUID(current_user.tenant_id)

    # Build query
    query = select(AuditEvent).where(AuditEvent.tenant_id == tenant_id)

    # Apply filters
    if event_type:
        query = query.where(AuditEvent.event_type == event_type)
    if actor_type:
        query = query.where(AuditEvent.actor_type == actor_type)
    if resource_id:
        query = query.where(AuditEvent.resource_id == resource_id)
    if start_date:
        query = query.where(AuditEvent.timestamp >= start_date)
    if end_date:
        query = query.where(AuditEvent.timestamp <= end_date)

    # Get total count (for pagination)
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and ordering
    query = query.order_by(AuditEvent.timestamp.desc()).offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    events = result.scalars().all()

    return AuditEventList(
        events=events,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/statistics", response_model=AuditStatistics)
async def get_audit_statistics(
    days: int = Query(30, ge=1, le=365),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get audit statistics for current tenant.

    Args:
        days: Number of days to analyze (default 30)

    Returns statistics including:
    - Total events
    - Events by type
    - Events by status
    - Recent activity trends
    """
    tenant_id = UUID(current_user.tenant_id)
    start_date = datetime.utcnow() - timedelta(days=days)

    # Total events
    total_query = select(func.count(AuditEvent.id)).where(
        and_(
            AuditEvent.tenant_id == tenant_id,
            AuditEvent.timestamp >= start_date,
        )
    )
    total_result = await db.execute(total_query)
    total_events = total_result.scalar() or 0

    # Events by type
    type_query = (
        select(AuditEvent.event_type, func.count(AuditEvent.id))
        .where(
            and_(
                AuditEvent.tenant_id == tenant_id,
                AuditEvent.timestamp >= start_date,
            )
        )
        .group_by(AuditEvent.event_type)
    )
    type_result = await db.execute(type_query)
    events_by_type = {str(event_type.value): count for event_type, count in type_result}

    # Events by status
    status_query = (
        select(AuditEvent.status, func.count(AuditEvent.id))
        .where(
            and_(
                AuditEvent.tenant_id == tenant_id,
                AuditEvent.timestamp >= start_date,
            )
        )
        .group_by(AuditEvent.status)
    )
    status_result = await db.execute(status_query)
    events_by_status = {status: count for status, count in status_result}

    # Events by actor type
    actor_query = (
        select(AuditEvent.actor_type, func.count(AuditEvent.id))
        .where(
            and_(
                AuditEvent.tenant_id == tenant_id,
                AuditEvent.timestamp >= start_date,
            )
        )
        .group_by(AuditEvent.actor_type)
    )
    actor_result = await db.execute(actor_query)
    events_by_actor = {actor_type: count for actor_type, count in actor_result}

    return AuditStatistics(
        total_events=total_events,
        events_by_type=events_by_type,
        events_by_status=events_by_status,
        events_by_actor=events_by_actor,
        period_days=days,
        start_date=start_date,
        end_date=datetime.utcnow(),
    )


@router.get("/user/{user_id}", response_model=AuditEventList)
async def get_user_activity(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get audit events for a specific user.

    Useful for:
    - User activity reports
    - GDPR data access requests
    - Security investigations
    """
    tenant_id = UUID(current_user.tenant_id)

    # Only admins can view other users' activity
    if str(user_id) != current_user.user_id and current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view other users' activity",
        )

    # Query user's events
    query = (
        select(AuditEvent)
        .where(
            and_(
                AuditEvent.tenant_id == tenant_id,
                AuditEvent.user_id == user_id,
            )
        )
        .order_by(AuditEvent.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )

    # Get total count
    count_query = select(func.count(AuditEvent.id)).where(
        and_(
            AuditEvent.tenant_id == tenant_id,
            AuditEvent.user_id == user_id,
        )
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Execute query
    result = await db.execute(query)
    events = result.scalars().all()

    return AuditEventList(
        events=events,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/resource/{resource_type}/{resource_id}", response_model=AuditEventList)
async def get_resource_history(
    resource_type: str,
    resource_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get audit history for a specific resource (project, document, etc.).

    Shows all actions performed on this resource:
    - Who created it
    - Who modified it
    - What AI agents analyzed it
    - When it was accessed

    Useful for:
    - Change tracking
    - Compliance audits
    - Debugging issues
    """
    tenant_id = UUID(current_user.tenant_id)

    # Query resource events
    query = (
        select(AuditEvent)
        .where(
            and_(
                AuditEvent.tenant_id == tenant_id,
                AuditEvent.resource_type == resource_type,
                AuditEvent.resource_id == resource_id,
            )
        )
        .order_by(AuditEvent.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )

    # Get total count
    count_query = select(func.count(AuditEvent.id)).where(
        and_(
            AuditEvent.tenant_id == tenant_id,
            AuditEvent.resource_type == resource_type,
            AuditEvent.resource_id == resource_id,
        )
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Execute query
    result = await db.execute(query)
    events = result.scalars().all()

    return AuditEventList(
        events=events,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/ai-activity", response_model=AuditEventList)
async def get_ai_activity(
    agent_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get AI agent activity for current tenant.

    Shows:
    - Which AI agents ran
    - What documents they analyzed
    - Confidence scores
    - Token usage
    - Processing times

    Useful for:
    - Monitoring AI performance
    - Understanding AI costs
    - Debugging AI issues
    """
    tenant_id = UUID(current_user.tenant_id)

    # Build query
    query = select(AuditEvent).where(
        and_(
            AuditEvent.tenant_id == tenant_id,
            AuditEvent.event_type.in_([EventType.AI_AGENT, EventType.AI_ANALYSIS]),
        )
    )

    # Filter by agent type if specified
    if agent_type:
        query = query.where(AuditEvent.actor_id == agent_type)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(AuditEvent.timestamp.desc()).offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    events = result.scalars().all()

    return AuditEventList(
        events=events,
        total=total,
        skip=skip,
        limit=limit,
    )

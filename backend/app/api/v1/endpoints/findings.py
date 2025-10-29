"""
Compliance findings endpoints.

Provides CRUD operations for findings (AI-generated compliance issues,
recommendations, and observations).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional, List

from ....db.base import get_db
from ....models.user import User
from ....models.finding import Finding, FindingType, FindingSeverity, FindingStatus
from ....models.document import Document
from ....models.project import Project
from ....schemas.finding import (
    Finding as FindingSchema,
    FindingCreate,
    FindingUpdate,
    FindingsList,
    FindingsSummary,
)
from ....core.deps import get_current_user
from ....services.audit_logger import audit_logger
from ....models.audit import EventType
from ....middleware import ResourceNotFoundError, TenantIsolationError

router = APIRouter()


@router.post("/", response_model=FindingSchema, status_code=status.HTTP_201_CREATED)
async def create_finding(
    finding_data: FindingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new compliance finding.

    Typically called by AI agents during document analysis.
    """
    # Verify document exists and user has access
    result = await db.execute(
        select(Document).where(
            Document.id == finding_data.document_id,
            Document.tenant_id == current_user.tenant_id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise ResourceNotFoundError("Document", str(finding_data.document_id))

    # Create finding
    finding = Finding(
        tenant_id=current_user.tenant_id,
        project_id=document.project_id,
        document_id=document.id,
        **finding_data.model_dump(),
    )

    db.add(finding)
    await db.commit()
    await db.refresh(finding)

    # Log audit event
    await audit_logger.log_event(
        tenant_id=current_user.tenant_id,
        event_type=EventType.AI_OPERATION,
        action="create_finding",
        actor_type="ai_agent",
        actor_id=finding_data.specialist_agent,
        user_id=current_user.id,
        status="success",
        description=f"AI agent '{finding_data.specialist_agent}' created finding: {finding.title}",
        resource_type="finding",
        resource_id=finding.id,
        metadata={
            "severity": finding.severity.value,
            "category": finding.category,
        },
    )

    return finding


@router.get("/", response_model=FindingsList)
async def list_findings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    project_id: Optional[UUID] = Query(None, description="Filter by project"),
    document_id: Optional[UUID] = Query(None, description="Filter by document"),
    severity: Optional[FindingSeverity] = Query(None, description="Filter by severity"),
    status_filter: Optional[FindingStatus] = Query(None, alias="status", description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by regulation category"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Results per page"),
):
    """
    List compliance findings with filters.

    Supports filtering by:
    - Project
    - Document
    - Severity (critical, major, minor, info)
    - Status (open, in_review, resolved, dismissed)
    - Category (regulation part)

    Includes pagination.
    """
    # Base query with tenant isolation
    query = select(Finding).where(Finding.tenant_id == current_user.tenant_id)

    # Apply filters
    if project_id:
        query = query.where(Finding.project_id == project_id)

    if document_id:
        query = query.where(Finding.document_id == document_id)

    if severity:
        query = query.where(Finding.severity == severity)

    if status_filter:
        query = query.where(Finding.status == status_filter)

    if category:
        query = query.where(Finding.category.ilike(f"%{category}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Finding.created_at.desc())

    # Execute query
    result = await db.execute(query)
    findings = result.scalars().all()

    # Calculate pages
    pages = (total + page_size - 1) // page_size

    return FindingsList(
        findings=findings,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/summary", response_model=FindingsSummary)
async def get_findings_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    project_id: Optional[UUID] = Query(None, description="Filter by project"),
    document_id: Optional[UUID] = Query(None, description="Filter by document"),
):
    """
    Get summary statistics for findings.

    Returns aggregated counts by:
    - Severity
    - Status
    - Category (regulation part)
    - Specialist agent

    Useful for dashboards and compliance overview.
    """
    # Base query with tenant isolation
    query = select(Finding).where(Finding.tenant_id == current_user.tenant_id)

    # Apply filters
    if project_id:
        query = query.where(Finding.project_id == project_id)

    if document_id:
        query = query.where(Finding.document_id == document_id)

    # Get all findings
    result = await db.execute(query)
    findings = result.scalars().all()

    # Calculate statistics
    total_findings = len(findings)

    # Group by severity
    by_severity = {}
    for severity in FindingSeverity:
        by_severity[severity.value] = sum(1 for f in findings if f.severity == severity)

    # Group by status
    by_status = {}
    for status_enum in FindingStatus:
        by_status[status_enum.value] = sum(1 for f in findings if f.status == status_enum)

    # Group by category
    by_category = {}
    for finding in findings:
        category = finding.category
        by_category[category] = by_category.get(category, 0) + 1

    # Group by agent
    by_agent = {}
    for finding in findings:
        agent = finding.specialist_agent
        by_agent[agent] = by_agent.get(agent, 0) + 1

    return FindingsSummary(
        total_findings=total_findings,
        by_severity=by_severity,
        by_status=by_status,
        by_category=by_category,
        by_agent=by_agent,
    )


@router.get("/{finding_id}", response_model=FindingSchema)
async def get_finding(
    finding_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific finding by ID.

    Enforces tenant isolation.
    """
    result = await db.execute(
        select(Finding).where(
            Finding.id == finding_id,
            Finding.tenant_id == current_user.tenant_id,
        )
    )
    finding = result.scalar_one_or_none()

    if not finding:
        raise ResourceNotFoundError("Finding", str(finding_id))

    return finding


@router.patch("/{finding_id}", response_model=FindingSchema)
async def update_finding(
    finding_id: UUID,
    finding_update: FindingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a finding.

    Allows updating:
    - Status (e.g., marking as resolved)
    - Severity (if engineer disagrees with AI)
    - Description and recommendation
    - Metadata

    Typically used by engineers reviewing AI findings.
    """
    # Get finding with tenant isolation
    result = await db.execute(
        select(Finding).where(
            Finding.id == finding_id,
            Finding.tenant_id == current_user.tenant_id,
        )
    )
    finding = result.scalar_one_or_none()

    if not finding:
        raise ResourceNotFoundError("Finding", str(finding_id))

    # Update only provided fields
    update_data = finding_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(finding, field, value)

    await db.commit()
    await db.refresh(finding)

    # Log audit event
    await audit_logger.log_user_action(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="update_finding",
        event_type=EventType.DOCUMENT_OPERATION,
        status="success",
        description=f"User updated finding: {finding.title}",
        resource_type="finding",
        resource_id=finding.id,
        metadata={"updated_fields": list(update_data.keys())},
    )

    return finding


@router.delete("/{finding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_finding(
    finding_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a finding.

    Typically used to remove false positives or irrelevant findings.
    """
    # Get finding with tenant isolation
    result = await db.execute(
        select(Finding).where(
            Finding.id == finding_id,
            Finding.tenant_id == current_user.tenant_id,
        )
    )
    finding = result.scalar_one_or_none()

    if not finding:
        raise ResourceNotFoundError("Finding", str(finding_id))

    # Log audit event before deletion
    await audit_logger.log_user_action(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="delete_finding",
        event_type=EventType.DOCUMENT_OPERATION,
        status="success",
        description=f"User deleted finding: {finding.title}",
        resource_type="finding",
        resource_id=finding.id,
    )

    # Delete finding
    await db.delete(finding)
    await db.commit()

    return None

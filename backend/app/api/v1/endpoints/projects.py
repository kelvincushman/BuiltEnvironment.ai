"""
Project endpoints for creating and managing building projects.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from ....db.base import get_db
from ....models.project import Project, ProjectStatus
from ....models.user import User
from ....schemas.project import Project as ProjectSchema, ProjectCreate, ProjectUpdate
from ....core.security import CurrentUser
from ....core.deps import get_current_user
from ....services.audit_logger import audit_logger
from ....services.usage_tracker import usage_tracker
from ....models.audit import EventType

router = APIRouter()


@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new building project.

    Enforces project limit based on subscription tier.
    """
    # Check project limit before creating
    await usage_tracker.check_project_limit(current_user.tenant_id, db)

    # Create project
    project = Project(
        tenant_id=current_user.tenant_id,
        name=project_data.name,
        description=project_data.description,
        reference_number=project_data.reference_number,
        address_line1=project_data.address_line1,
        address_line2=project_data.address_line2,
        city=project_data.city,
        postcode=project_data.postcode,
        country=project_data.country,
        project_type=project_data.project_type,
        building_use=project_data.building_use,
        status=ProjectStatus.DRAFT,
        compliance_summary={},
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    # Log project creation audit event
    await audit_logger.log_user_action(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="create",
        event_type=EventType.USER_ACTION,
        status="success",
        description=f"Created project '{project.name}'",
        resource_type="project",
        resource_id=project.id,
    )

    return project


@router.get("/", response_model=List[ProjectSchema])
async def list_projects(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all projects for the current tenant.
    """

    result = await db.execute(
        select(Project)
        .where(Project.tenant_id == current_user.tenant_id)
        .order_by(Project.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    projects = result.scalars().all()

    return projects


@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific project by ID.
    """

    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.patch("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a project's information.
    """

    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Update fields if provided
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a project and all associated documents.

    Only administrators can delete projects.
    """

    # Only admins can delete projects
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete projects",
        )

    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    await db.delete(project)
    await db.commit()

    return None

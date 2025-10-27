"""
Document endpoints for uploading and managing building documents.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID, uuid4
import os
import shutil
from pathlib import Path

from ....db.base import get_db
from ....models.document import Document, DocumentStatus, DocumentType
from ....models.project import Project
from ....schemas.document import Document as DocumentSchema, DocumentUpdate
from ....core.security import CurrentUser
from ....core.config import settings

router = APIRouter()


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return Path(filename).suffix.lower()


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    ext = get_file_extension(file.filename)

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {ext} not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    # Note: file.size might not be available in all cases
    # We'll check after writing to disk if needed


async def save_upload_file(
    upload_file: UploadFile, tenant_id: str, project_id: str
) -> tuple[str, str, int]:
    """
    Save uploaded file to disk.
    Returns (file_path, filename, file_size)
    """
    # Create directory structure: uploads/{tenant_id}/{project_id}/
    upload_dir = Path(settings.UPLOAD_DIR) / tenant_id / project_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    ext = get_file_extension(upload_file.filename)
    unique_filename = f"{uuid4()}{ext}"
    file_path = upload_dir / unique_filename

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    # Get file size
    file_size = os.path.getsize(file_path)

    # Check file size limit
    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    return str(file_path), unique_filename, file_size


@router.post("/upload", response_model=DocumentSchema, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: UUID = Form(...),
    document_type: Optional[str] = Form("other"),
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a document to a project.

    This endpoint:
    1. Validates the file
    2. Saves it to disk
    3. Creates a database record
    4. Triggers async processing (text extraction, AI analysis)
    """

    # Validate file
    validate_file(file)

    # Check project exists and user has access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.tenant_id == UUID(current_user.tenant_id),
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Save file
    file_path, filename, file_size = await save_upload_file(
        file, current_user.tenant_id, str(project_id)
    )

    # Create document record
    document = Document(
        tenant_id=UUID(current_user.tenant_id),
        project_id=project_id,
        filename=filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        file_extension=get_file_extension(file.filename),
        document_type=DocumentType(document_type) if document_type else DocumentType.OTHER,
        status=DocumentStatus.UPLOADED,
        ai_analysis={},
        compliance_findings={},
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    # TODO: Trigger async processing
    # - Extract text from PDF/DOCX
    # - Index in ChromaDB
    # - Run AI analysis
    # - Generate compliance findings

    return document


@router.get("/", response_model=List[DocumentSchema])
async def list_documents(
    project_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    List documents for the current tenant.
    Optionally filter by project_id.
    """

    query = select(Document).where(Document.tenant_id == UUID(current_user.tenant_id))

    if project_id:
        query = query.where(Document.project_id == project_id)

    query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    documents = result.scalars().all()

    return documents


@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(
    document_id: UUID,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific document by ID.
    """

    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == UUID(current_user.tenant_id),
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.patch("/{document_id}", response_model=DocumentSchema)
async def update_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Update document metadata (type, engineer notes).
    """

    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == UUID(current_user.tenant_id),
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Update fields
    update_data = document_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "document_type" and value:
            setattr(document, field, DocumentType(value))
        else:
            setattr(document, field, value)

    await db.commit()
    await db.refresh(document)

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a document and its associated file.
    """

    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == UUID(current_user.tenant_id),
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Delete file from disk
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete database record
    await db.delete(document)
    await db.commit()

    return None

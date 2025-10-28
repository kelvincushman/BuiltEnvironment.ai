"""
Document endpoints for uploading and managing building documents.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID, uuid4
import os
import shutil
from pathlib import Path
import mimetypes

from ....db.base import get_db
from ....models.document import Document, DocumentStatus, DocumentType
from ....models.project import Project
from ....schemas.document import Document as DocumentSchema, DocumentUpdate
from ....core.security import CurrentUser
from ....core.config import settings
from ....services.storage_service import storage_service
from ....services.text_extraction_service import text_extraction_service
from ....services.usage_tracker import usage_tracker
from ....services.audit_logger import audit_logger
from ....models.audit import EventType
from ....schemas.document import DocumentUploadResponse

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


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
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
    1. Checks usage limits (documents and storage)
    2. Validates the file type
    3. Saves file to storage
    4. Extracts text (PDF/images)
    5. Creates database record
    6. Logs audit event
    7. Returns document with extraction status
    """
    tenant_id = UUID(current_user.tenant_id)
    user_id = UUID(current_user.user_id)

    # Validate file extension
    if not storage_service.is_allowed_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(storage_service.get_allowed_extensions())}",
        )

    # Check project exists and user has access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.tenant_id == tenant_id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check document limit
    await usage_tracker.check_document_limit(tenant_id, db)

    # Read file content and check size
    file_content = await file.read()
    file_size = len(file_content)

    # Check storage limit
    await usage_tracker.check_storage_limit(tenant_id, file_size, db)

    # Check max file size
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Create document ID
    document_id = uuid4()

    # Save file to storage
    from io import BytesIO
    file_obj = BytesIO(file_content)

    save_result = await storage_service.save_file(
        file=file_obj,
        tenant_id=tenant_id,
        project_id=project_id,
        document_id=document_id,
        filename=file.filename,
    )

    # Get MIME type
    mime_type = storage_service.get_mime_type(file.filename)

    # Create document record
    document = Document(
        id=document_id,
        tenant_id=tenant_id,
        project_id=project_id,
        filename=Path(save_result["file_path"]).name,
        original_filename=file.filename,
        file_path=save_result["file_path"],
        file_size=save_result["file_size"],
        mime_type=mime_type,
        file_extension=get_file_extension(file.filename),
        document_type=DocumentType(document_type) if document_type else DocumentType.OTHER,
        status=DocumentStatus.PROCESSING,
        ai_analysis={},
        compliance_findings={},
    )

    db.add(document)
    await db.commit()

    # Extract text in background (non-blocking for user)
    extraction_status = "pending"
    pages_extracted = None

    try:
        extraction_result = await text_extraction_service.extract_from_file(
            file_path=Path(save_result["file_path"]),
            mime_type=mime_type,
        )

        # Update document with extracted text
        document.extracted_text = extraction_result["text"]
        document.page_count = extraction_result["page_count"]
        document.status = DocumentStatus.INDEXED
        document.processed_at = None  # Will be set after AI analysis

        await db.commit()

        extraction_status = extraction_result["method"]
        pages_extracted = extraction_result["page_count"]

    except Exception as e:
        # Don't fail upload if text extraction fails
        import logging
        logging.error(f"Text extraction failed: {e}")
        extraction_status = "failed"
        document.status = DocumentStatus.UPLOADED
        await db.commit()

    await db.refresh(document)

    # Log audit event
    await audit_logger.log_user_action(
        tenant_id=tenant_id,
        user_id=user_id,
        action="upload",
        event_type=EventType.DOCUMENT_UPLOAD,
        status="success",
        description=f"Uploaded document '{file.filename}' to project '{project.name}'",
        resource_type="document",
        resource_id=document.id,
    )

    return DocumentUploadResponse(
        document=document,
        message="Document uploaded and processed successfully",
        extraction_status=extraction_status,
        pages_extracted=pages_extracted,
    )


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


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Download a document file.

    Returns the file with appropriate headers for download or inline viewing.
    """
    tenant_id = UUID(current_user.tenant_id)
    user_id = UUID(current_user.user_id)

    # Get document
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == tenant_id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check if file exists
    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on disk",
        )

    # Log download audit event
    await audit_logger.log_user_action(
        tenant_id=tenant_id,
        user_id=user_id,
        action="download",
        event_type=EventType.DOCUMENT_DOWNLOAD,
        status="success",
        description=f"Downloaded document '{document.original_filename}'",
        resource_type="document",
        resource_id=document.id,
    )

    # Return file with proper headers
    return FileResponse(
        path=file_path,
        media_type=document.mime_type or "application/octet-stream",
        filename=document.original_filename,
        headers={
            "Content-Disposition": f'attachment; filename="{document.original_filename}"'
        }
    )


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
    tenant_id = UUID(current_user.tenant_id)
    user_id = UUID(current_user.user_id)

    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == tenant_id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Track what changed for audit log
    changes = []
    update_data = document_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "document_type" and value:
            old_value = document.document_type.value if document.document_type else None
            new_value = value
            if old_value != new_value:
                changes.append(f"{field}: {old_value} → {new_value}")
            setattr(document, field, DocumentType(value))
        else:
            old_value = getattr(document, field)
            if old_value != value:
                changes.append(f"{field}: updated")
            setattr(document, field, value)

    await db.commit()
    await db.refresh(document)

    # Log audit event
    if changes:
        await audit_logger.log_user_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="update",
            event_type=EventType.DOCUMENT_UPDATE,
            status="success",
            description=f"Updated document '{document.original_filename}': {', '.join(changes)}",
            resource_type="document",
            resource_id=document.id,
        )

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a document and its associated file.

    This permanently removes:
    - The file from storage
    - The database record
    - Any associated metadata
    """
    tenant_id = UUID(current_user.tenant_id)
    user_id = UUID(current_user.user_id)

    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == tenant_id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Store info for audit log before deletion
    filename = document.original_filename
    file_size = document.file_size

    # Delete file from storage using storage service
    try:
        await storage_service.delete_file(
            tenant_id=tenant_id,
            project_id=document.project_id,
            document_id=document_id,
            filename=document.filename,
        )
    except Exception as e:
        # Log error but continue with database deletion
        import logging
        logging.error(f"Failed to delete file from storage: {e}")

    # Delete database record
    await db.delete(document)
    await db.commit()

    # Log audit event
    await audit_logger.log_user_action(
        tenant_id=tenant_id,
        user_id=user_id,
        action="delete",
        event_type=EventType.DOCUMENT_DELETE,
        status="success",
        description=f"Deleted document '{filename}' ({file_size} bytes)",
        resource_type="document",
        resource_id=document_id,
    )

    return None

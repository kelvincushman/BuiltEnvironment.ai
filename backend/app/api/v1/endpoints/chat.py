"""
Chat endpoints for RAG-powered document Q&A.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from ....db.base import get_db
from ....models.document import Document
from ....models.project import Project
from ....core.security import CurrentUser
from ....services.rag_service import RAGService, ChatService

router = APIRouter()

# Initialize services
rag_service = RAGService()
chat_service = ChatService(rag_service)


class ChatMessage(BaseModel):
    """Chat message schema."""

    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request schema."""

    query: str
    document_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    conversation_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    """Chat response schema."""

    response: str
    sources: List[dict]
    metadata: dict


class ProcessDocumentRequest(BaseModel):
    """Request to process and index a document."""

    document_id: UUID


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Chat with documents using RAG-powered AI.

    Can chat with:
    - Specific document (document_id)
    - All documents in a project (project_id)
    - All documents in tenant (no filters)
    """

    # Validate document/project access if specified
    if request.document_id:
        result = await db.execute(
            select(Document).where(
                Document.id == request.document_id,
                Document.tenant_id == UUID(current_user.tenant_id),
            )
        )
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

    elif request.project_id:
        result = await db.execute(
            select(Project).where(
                Project.id == request.project_id,
                Project.tenant_id == UUID(current_user.tenant_id),
            )
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

    # Convert conversation history to dict format
    conversation = None
    if request.conversation_history:
        conversation = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

    # Generate response
    result = await chat_service.generate_response(
        tenant_id=current_user.tenant_id,
        user_query=request.query,
        document_id=str(request.document_id) if request.document_id else None,
        conversation_history=conversation,
    )

    return ChatResponse(**result)


@router.post("/process-document", status_code=status.HTTP_202_ACCEPTED)
async def process_document(
    request: ProcessDocumentRequest,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Process and index a document for RAG chat.

    This endpoint:
    1. Extracts text from the document
    2. Chunks the text
    3. Generates embeddings
    4. Indexes in ChromaDB
    """

    # Get document
    result = await db.execute(
        select(Document).where(
            Document.id == request.document_id,
            Document.tenant_id == UUID(current_user.tenant_id),
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Extract text if not already extracted
    if not document.extracted_text:
        from ....services.document_processor import DocumentProcessor

        extracted_text, page_count = DocumentProcessor.extract_text(
            document.file_path, document.file_extension
        )

        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from document",
            )

        # Clean text
        extracted_text = DocumentProcessor.clean_text(extracted_text)

        # Update document
        document.extracted_text = extracted_text
        document.page_count = page_count

        # Extract metadata
        metadata = DocumentProcessor.extract_metadata(extracted_text)
        document.ai_analysis["extracted_metadata"] = metadata

        await db.commit()

    # Chunk text
    from ....services.document_processor import DocumentProcessor

    chunks = DocumentProcessor.chunk_text(
        document.extracted_text,
        chunk_size=1000,
        chunk_overlap=200,
    )

    # Index in ChromaDB
    document_metadata = {
        "filename": document.original_filename,
        "document_type": document.document_type.value,
        "project_id": str(document.project_id),
    }

    indexing_result = rag_service.index_document(
        tenant_id=current_user.tenant_id,
        document_id=str(document.id),
        chunks=chunks,
        document_metadata=document_metadata,
    )

    # Update document with vector indexing info
    document.vector_indexed = {
        **indexing_result,
        "indexed_at": datetime.utcnow().isoformat(),
        "embedding_model": "text-embedding-3-small",
    }
    document.status = "indexed"

    await db.commit()

    return {
        "message": "Document processed and indexed successfully",
        "document_id": str(document.id),
        "chunks_indexed": indexing_result["chunk_count"],
    }


@router.get("/collection-stats")
async def get_collection_stats(
    current_user: CurrentUser = Depends(),
):
    """
    Get RAG collection statistics for current tenant.
    """

    stats = rag_service.get_collection_stats(current_user.tenant_id)

    return stats


# Import datetime at top of file
from datetime import datetime

"""
AI Agent endpoints for document compliance analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from ....db.base import get_db
from ....models.document import Document, DocumentStatus
from ....models.audit import AuditEvent, EventType
from ....core.security import CurrentUser
from ....services.ai_agents.fire_safety_agent import FireSafetyAgent

router = APIRouter()


class AnalyzeDocumentRequest(BaseModel):
    """Request to analyze a document."""

    document_id: UUID
    agent_type: str = "fire_safety"  # For MVP, only fire_safety available


class AnalyzeDocumentResponse(BaseModel):
    """Response from document analysis."""

    document_id: UUID
    status: str
    message: str
    analysis: Optional[dict] = None


async def run_ai_analysis(
    document_id: UUID,
    tenant_id: str,
    user_id: str,
    db: AsyncSession,
):
    """
    Background task to run AI analysis on a document.
    """
    try:
        # Get document
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document or not document.extracted_text:
            return

        # Update status
        document.status = DocumentStatus.PROCESSING
        await db.commit()

        # Run Fire Safety Agent
        agent = FireSafetyAgent()

        document_metadata = {
            "filename": document.original_filename,
            "document_type": document.document_type.value,
            "file_size": document.file_size,
        }

        analysis_result = await agent.analyze(
            document_text=document.extracted_text,
            document_metadata=document_metadata,
        )

        # Update document with analysis results
        document.ai_analysis = analysis_result

        # Create compliance findings in the expected format
        compliance_findings = {
            "overall_status": analysis_result["overall_status"],
            "confidence_score": analysis_result["confidence_score"],
            "reasoning": analysis_result["reasoning"],
            "findings": [],
            "green_count": 0,
            "amber_count": 0,
            "red_count": 0,
        }

        # Transform compliance_findings into traffic light format
        for finding in analysis_result["compliance_findings"]:
            status = finding["status"].lower()
            compliance_findings["findings"].append({
                "regulation": f"Part {finding['requirement_id']}",
                "requirement": finding["requirement_title"],
                "status": status,
                "confidence": finding["confidence"],
                "evidence": finding.get("evidence", ""),
                "issues": finding.get("issues", []),
                "recommendations": finding.get("recommendations", []),
            })

            # Count status types
            if status == "green":
                compliance_findings["green_count"] += 1
            elif status == "amber":
                compliance_findings["amber_count"] += 1
            elif status == "red":
                compliance_findings["red_count"] += 1

        document.compliance_findings = compliance_findings
        document.status = DocumentStatus.AI_ANALYSIS_COMPLETE
        document.processed_at = datetime.utcnow()

        await db.commit()

        # Log audit event
        audit_event = AuditEvent(
            tenant_id=UUID(tenant_id),
            user_id=UUID(user_id),
            event_type=EventType.AI_ANALYSIS,
            action="fire_safety_analysis",
            status="success",
            description=f"Fire safety analysis completed for document {document.original_filename}",
            resource_type="document",
            resource_id=document_id,
            actor_type="ai_agent",
            actor_id="fire_safety_agent_v1",
            ai_metadata={
                "agent_type": "fire_safety",
                "overall_status": analysis_result["overall_status"],
                "confidence_score": analysis_result["confidence_score"],
                "findings_count": len(analysis_result["compliance_findings"]),
                "model_used": analysis_result["model_used"],
            },
        )
        db.add(audit_event)
        await db.commit()

    except Exception as e:
        # Handle errors
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        if document:
            document.status = DocumentStatus.ERROR
            document.ai_analysis = {"error": str(e)}
            await db.commit()


@router.post("/analyze", response_model=AnalyzeDocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def analyze_document(
    request: AnalyzeDocumentRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze a document for compliance using AI agents.

    This endpoint triggers background processing:
    1. Extracts text if not already done
    2. Runs Fire Safety Agent (Part B compliance)
    3. Generates traffic light findings (Green/Amber/Red)
    4. Stores results in document.compliance_findings

    Returns immediately with 202 Accepted.
    Check document status to see when analysis is complete.
    """

    # Validate agent type
    if request.agent_type != "fire_safety":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only 'fire_safety' agent is available in MVP",
        )

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

    # Check if text is extracted
    if not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document text must be extracted first. Call POST /chat/process-document",
        )

    # Trigger background analysis
    background_tasks.add_task(
        run_ai_analysis,
        request.document_id,
        current_user.tenant_id,
        current_user.user_id,
        db,
    )

    return AnalyzeDocumentResponse(
        document_id=request.document_id,
        status="processing",
        message="AI analysis started. Check document status for completion.",
    )


@router.get("/agents")
async def list_agents(current_user: CurrentUser = Depends()):
    """
    List available AI agents.
    """

    return {
        "agents": [
            {
                "id": "fire_safety",
                "name": "Fire Safety Agent",
                "description": "Analyzes documents against UK Building Regulations Part B (Fire Safety)",
                "version": "1.0.0",
                "regulations_covered": ["B1", "B2", "B3", "B4", "B5"],
                "available": True,
            },
            # Future agents (not yet implemented):
            {
                "id": "structural",
                "name": "Structural Agent",
                "description": "Part A - Structure analysis",
                "available": False,
            },
            {
                "id": "accessibility",
                "name": "Accessibility Agent",
                "description": "Part M - Access and use analysis",
                "available": False,
            },
        ]
    }

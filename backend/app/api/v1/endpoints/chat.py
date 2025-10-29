"""
Chat endpoints for AI-powered document conversations.

Supports:
- Creating and managing conversations
- Sending messages and receiving AI responses
- WebSocket streaming for real-time responses
- Specialist agent selection
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from uuid import UUID, uuid4
import logging

from ....db.base import get_db
from ....models.chat import Conversation, Message, ConversationStatus, MessageRole
from ....models.project import Project
from ....models.user import User
from ....schemas.chat import (
    ConversationCreate,
    ConversationUpdate,
    ConversationSummary,
    ConversationDetail,
    ConversationList,
    MessageResponse,
    MessageFeedback,
    ChatRequest,
    ChatResponse,
    SpecialistAgentList,
    SpecialistAgentInfo,
)
from ....core.security import CurrentUser
from ....core.deps import get_current_user
from ....services.chat_service import chat_service
from ....services.usage_tracker import usage_tracker
from ....services.audit_logger import audit_logger
from ....models.audit import EventType

logger = logging.getLogger(__name__)

router = APIRouter()


# ===== Specialist Agents =====

@router.get("/agents", response_model=SpecialistAgentList)
async def list_specialist_agents():
    """
    Get list of available specialist AI agents.

    Returns information about each specialist agent including:
    - Agent ID and name
    - UK Building Regulations coverage
    - Specialties and focus areas
    """
    agents_data = chat_service.get_specialist_agents()

    agents = [
        SpecialistAgentInfo(
            agent_id=agent["agent_id"],
            name=agent["name"],
            description=agent["description"],
            uk_building_parts=agent["uk_building_parts"],
            specialties=agent["specialties"],
        )
        for agent in agents_data
    ]

    return SpecialistAgentList(agents=agents)


# ===== Conversations =====

@router.post("/conversations", response_model=ConversationDetail, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new conversation.

    A conversation is a thread of messages between user and AI agents.
    """
    tenant_id = UUID(current_user.tenant_id)
    user_id = UUID(current_user.user_id)

    # Verify project exists and user has access
    result = await db.execute(
        select(Project).where(
            Project.id == conversation_data.project_id,
            Project.tenant_id == tenant_id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Create conversation
    conversation = Conversation(
        id=uuid4(),
        tenant_id=tenant_id,
        project_id=conversation_data.project_id,
        user_id=user_id,
        title=conversation_data.title or "New Conversation",
        specialist_agent=conversation_data.specialist_agent or "general",
        document_ids=conversation_data.document_ids or [],
        status=ConversationStatus.ACTIVE,
        message_count=0,
    )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    # Log audit event
    await audit_logger.log_user_action(
        tenant_id=tenant_id,
        user_id=user_id,
        action="create_conversation",
        event_type=EventType.USER_ACTION,
        status="success",
        description=f"Created conversation '{conversation.title}' with {conversation.specialist_agent} agent",
        resource_type="conversation",
        resource_id=conversation.id,
    )

    return conversation


@router.get("/conversations", response_model=ConversationList)
async def list_conversations(
    project_id: Optional[UUID] = None,
    status_filter: Optional[ConversationStatus] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    List conversations for the current tenant.

    Optionally filter by project and status.
    """
    tenant_id = UUID(current_user.tenant_id)

    # Build query
    query = select(Conversation).where(Conversation.tenant_id == tenant_id)

    if project_id:
        query = query.where(Conversation.project_id == project_id)

    if status_filter:
        query = query.where(Conversation.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get conversations
    query = query.order_by(Conversation.updated_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    conversations = result.scalars().all()

    return ConversationList(
        conversations=conversations,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a conversation with all its messages.
    """
    tenant_id = UUID(current_user.tenant_id)

    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Load messages
    messages_result = await db.execute(
        select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())
    )
    messages = messages_result.scalars().all()

    # Attach messages to conversation
    conversation.messages = messages

    return conversation


@router.patch("/conversations/{conversation_id}", response_model=ConversationDetail)
async def update_conversation(
    conversation_id: UUID,
    conversation_data: ConversationUpdate,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a conversation (title, status, agent, etc.).
    """
    tenant_id = UUID(current_user.tenant_id)

    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Update fields
    update_data = conversation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conversation, field, value)

    await db.commit()
    await db.refresh(conversation)

    return conversation


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a conversation and all its messages.
    """
    tenant_id = UUID(current_user.tenant_id)

    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    await db.delete(conversation)
    await db.commit()

    return None


# ===== Chat / Messaging =====

@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message and get AI response.

    This endpoint:
    1. Checks AI check limit (subscription enforcement) ✅
    2. Creates or retrieves conversation
    3. Saves user message
    4. Retrieves RAG context
    5. Generates AI response with specialist agent
    6. Saves AI response
    7. Increments AI check counter ✅
    8. Returns response with context summary

    Usage limits enforced:
    - AI checks per month (based on subscription tier)
    """
    tenant_id = current_user.tenant_id
    user_id = current_user.id

    # Check AI check limit before generating response
    await usage_tracker.check_ai_check_limit(tenant_id, db)

    # Get or create conversation
    if chat_request.conversation_id:
        # Use existing conversation
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == chat_request.conversation_id,
                Conversation.tenant_id == tenant_id,
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

    else:
        # Create new conversation
        # Generate title from first message
        title = await chat_service.generate_conversation_title(chat_request.message)

        conversation = Conversation(
            id=uuid4(),
            tenant_id=tenant_id,
            project_id=chat_request.project_id,
            user_id=user_id,
            title=title,
            specialist_agent=chat_request.specialist_agent or "general",
            document_ids=chat_request.document_ids or [],
            status=ConversationStatus.ACTIVE,
            message_count=0,
        )

        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Save user message
    user_message = Message(
        id=uuid4(),
        conversation_id=conversation.id,
        tenant_id=tenant_id,
        role=MessageRole.USER,
        content=chat_request.message,
    )

    db.add(user_message)

    # Get conversation history for context (last 10 messages)
    history_result = await db.execute(
        select(Message).where(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.desc()).limit(10)
    )
    history_messages = list(reversed(history_result.scalars().all()))

    # Format history for Claude
    conversation_history = [
        {
            "role": msg.role.value,
            "content": msg.content
        }
        for msg in history_messages
    ]

    # Generate AI response
    ai_response_data = await chat_service.generate_response(
        user_message=chat_request.message,
        tenant_id=tenant_id,
        project_id=chat_request.project_id,
        specialist_agent=chat_request.specialist_agent or conversation.specialist_agent,
        document_ids=chat_request.document_ids,
        conversation_history=conversation_history,
    )

    # Save AI message
    ai_message = Message(
        id=uuid4(),
        conversation_id=conversation.id,
        tenant_id=tenant_id,
        role=MessageRole.ASSISTANT,
        content=ai_response_data["content"],
        rag_context=ai_response_data["rag_context"],
        ai_metadata=ai_response_data["ai_metadata"],
    )

    db.add(ai_message)

    # Update conversation
    conversation.message_count += 2
    conversation.last_message_at = func.now()

    await db.commit()
    await db.refresh(ai_message)

    # Increment AI check counter for usage tracking
    await usage_tracker.increment_ai_check_count(tenant_id, db)

    # Log audit event
    await audit_logger.log_user_action(
        tenant_id=tenant_id,
        user_id=user_id,
        action="ai_chat",
        event_type=EventType.AI_ANALYSIS,
        status="success",
        description=f"AI chat with {conversation.specialist_agent} agent",
        resource_type="conversation",
        resource_id=conversation.id,
        ai_metadata=ai_response_data["ai_metadata"],
    )

    # Prepare response
    return ChatResponse(
        conversation_id=conversation.id,
        message_id=ai_message.id,
        role=MessageRole.ASSISTANT,
        content=ai_response_data["content"],
        rag_context_summary={
            "chunks_retrieved": ai_response_data["rag_context"]["chunks_retrieved"],
            "sources": ai_response_data["rag_context"]["sources"],
        },
        ai_metadata=ai_response_data["ai_metadata"],
    )


# ===== Message Feedback =====

@router.post("/messages/{message_id}/feedback", status_code=status.HTTP_204_NO_CONTENT)
async def submit_message_feedback(
    message_id: UUID,
    feedback_data: MessageFeedback,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit feedback on an AI message.

    Helps improve AI responses over time.
    """
    tenant_id = UUID(current_user.tenant_id)

    result = await db.execute(
        select(Message).where(
            Message.id == message_id,
            Message.tenant_id == tenant_id,
        )
    )
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    # Update feedback
    message.user_feedback = feedback_data.feedback
    message.feedback_comment = feedback_data.comment

    await db.commit()

    return None


# ===== WebSocket Streaming =====

@router.websocket("/chat/stream")
async def chat_stream(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for streaming AI responses.

    Protocol:
    1. Client sends: {"message": "...", "conversation_id": "...", "project_id": "...", ...}
    2. Server streams: {"chunk": "partial text", "done": false}
    3. Server sends final: {"chunk": "", "done": true, "message_id": "..."}
    """
    await websocket.accept()

    try:
        # Receive chat request
        data = await websocket.receive_json()

        # TODO: Extract and validate auth token from WebSocket connection
        # For now, we'll require conversation_id which has tenant association

        conversation_id = data.get("conversation_id")
        if not conversation_id:
            await websocket.send_json({"error": "conversation_id required for streaming"})
            await websocket.close()
            return

        conversation_id = UUID(conversation_id)

        # Get conversation (validates tenant access)
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            await websocket.send_json({"error": "Conversation not found"})
            await websocket.close()
            return

        # Save user message
        user_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            tenant_id=conversation.tenant_id,
            role=MessageRole.USER,
            content=data["message"],
        )
        db.add(user_message)
        await db.commit()

        # Stream AI response
        full_response = ""
        ai_message_id = uuid4()

        async for chunk in chat_service.generate_response_stream(
            user_message=data["message"],
            tenant_id=conversation.tenant_id,
            project_id=conversation.project_id,
            specialist_agent=conversation.specialist_agent,
            document_ids=data.get("document_ids"),
            conversation_history=[],  # TODO: Load history
        ):
            full_response += chunk

            # Send chunk to client
            await websocket.send_json({
                "conversation_id": str(conversation.id),
                "message_id": str(ai_message_id),
                "chunk": chunk,
                "done": False,
            })

        # Save complete AI message
        ai_message = Message(
            id=ai_message_id,
            conversation_id=conversation.id,
            tenant_id=conversation.tenant_id,
            role=MessageRole.ASSISTANT,
            content=full_response,
        )
        db.add(ai_message)

        # Update conversation
        conversation.message_count += 2
        conversation.last_message_at = func.now()

        await db.commit()

        # Send completion
        await websocket.send_json({
            "conversation_id": str(conversation.id),
            "message_id": str(ai_message_id),
            "chunk": "",
            "done": True,
        })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass

    finally:
        try:
            await websocket.close()
        except:
            pass

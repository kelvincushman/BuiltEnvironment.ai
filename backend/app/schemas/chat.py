"""
Pydantic schemas for chat conversations and messages.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from ..models.chat import ConversationStatus, MessageRole


# ===== Message Schemas =====

class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")


class MessageResponse(BaseModel):
    """Schema for message in response."""
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    rag_context: Optional[Dict[str, Any]] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    user_feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MessageFeedback(BaseModel):
    """Schema for user feedback on a message."""
    feedback: str = Field(..., pattern="^(helpful|not_helpful|incorrect)$")
    comment: Optional[str] = Field(None, max_length=500)


# ===== Conversation Schemas =====

class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""
    project_id: UUID
    title: Optional[str] = Field(None, max_length=255, description="Conversation title (auto-generated if not provided)")
    specialist_agent: Optional[str] = Field(None, description="Which specialist agent to consult")
    document_ids: Optional[List[UUID]] = Field(default_factory=list, description="Documents to discuss")


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    title: Optional[str] = Field(None, max_length=255)
    status: Optional[ConversationStatus] = None
    specialist_agent: Optional[str] = None
    document_ids: Optional[List[UUID]] = None


class ConversationSummary(BaseModel):
    """Summary of a conversation (list view)."""
    id: UUID
    project_id: UUID
    title: str
    specialist_agent: Optional[str]
    status: ConversationStatus
    message_count: int
    last_message_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    """Full conversation with messages."""
    id: UUID
    project_id: UUID
    user_id: UUID
    title: str
    specialist_agent: Optional[str]
    status: ConversationStatus
    document_ids: List[UUID]
    message_count: int
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ConversationList(BaseModel):
    """Paginated list of conversations."""
    conversations: List[ConversationSummary]
    total: int
    skip: int
    limit: int


# ===== Chat Request/Response Schemas =====

class ChatRequest(BaseModel):
    """Request to chat with AI about documents."""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID, or None for new conversation")
    project_id: UUID = Field(..., description="Project context for the chat")
    specialist_agent: Optional[str] = Field(None, description="Which specialist agent to use (default: general)")
    document_ids: Optional[List[UUID]] = Field(None, description="Specific documents to query (optional)")
    stream: bool = Field(False, description="Stream response via WebSocket")


class ChatResponse(BaseModel):
    """Response from AI chat."""
    conversation_id: UUID
    message_id: UUID
    role: MessageRole = MessageRole.ASSISTANT
    content: str
    rag_context_summary: Optional[Dict[str, Any]] = Field(
        None,
        description="Summary of RAG context used (chunks count, sources)"
    )
    ai_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ChatStreamChunk(BaseModel):
    """Streaming chunk for WebSocket."""
    conversation_id: UUID
    message_id: UUID
    chunk: str  # Partial text content
    done: bool = False  # True when stream is complete


# ===== Agent Selection =====

class SpecialistAgentInfo(BaseModel):
    """Information about a specialist agent."""
    agent_id: str
    name: str
    description: str
    uk_building_parts: List[str]  # e.g., ["Part B", "Part B1-B5"]
    specialties: List[str]


class SpecialistAgentList(BaseModel):
    """List of available specialist agents."""
    agents: List[SpecialistAgentInfo]

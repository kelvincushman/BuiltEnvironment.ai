"""
Chat conversation models for AI-powered document analysis.

Supports:
- Multi-turn conversations per project
- Specialist agent selection
- RAG context integration
- Message history persistence
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, func, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from ..db.base import Base


class ConversationStatus(str, enum.Enum):
    """Conversation status."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MessageRole(str, enum.Enum):
    """Message role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(Base):
    """
    Chat conversation for a project.

    A conversation is a thread of messages between user and AI agents
    about specific documents or compliance topics.
    """

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Conversation details
    title = Column(String(255), nullable=False)  # Auto-generated from first message
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE, index=True)

    # Specialist agent context
    specialist_agent = Column(String(100), nullable=True)  # Which agent is being consulted
    """
    Specialist agents:
    - structural_engineering
    - fire_safety
    - accessibility
    - environmental_sustainability
    - etc.
    """

    # Document context (optional - can chat about multiple docs or general topics)
    document_ids = Column(JSONB, default=list)  # List of document UUIDs being discussed

    # Metadata
    message_count = Column(Integer, default=0)
    last_message_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="conversations")
    project = relationship("Project", back_populates="conversations")
    user = relationship("User", back_populates="conversations", foreign_keys=[user_id])
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation {self.title} ({self.message_count} messages)>"


class Message(Base):
    """
    Individual message in a conversation.

    Stores user questions and AI responses with full context.
    """

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Message content
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # RAG context used for this message
    rag_context = Column(JSONB, nullable=True)
    """
    RAG context structure:
    {
        "agent": "fire_safety",
        "chunks_retrieved": 5,
        "chunks": [
            {
                "text": "chunk text",
                "document_id": "uuid",
                "page_number": 3,
                "relevance_score": 0.89
            }
        ]
    }
    """

    # AI metadata
    ai_metadata = Column(JSONB, nullable=True)
    """
    AI metadata:
    {
        "model": "claude-3-5-sonnet-20241022",
        "tokens_input": 1234,
        "tokens_output": 567,
        "temperature": 0.7,
        "processing_time_ms": 2340,
        "confidence": 0.85
    }
    """

    # Feedback
    user_feedback = Column(String(20), nullable=True)  # "helpful", "not_helpful", "incorrect"
    feedback_comment = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    tenant = relationship("Tenant")
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message {self.role.value}: {preview}>"

"""
Audit logging service for tracking all system activities.

This service provides:
- Structured audit event logging
- Batch writing for performance
- Automatic request tracking
- AI agent activity logging
- Compliance event tracking
"""

import asyncio
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.audit import AuditEvent, EventType
from ..db.base import async_session

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Centralized audit logging service with batch writing support.

    Usage:
        # Log a user action
        await audit_logger.log_user_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="create_project",
            resource_type="project",
            resource_id=project_id,
            description="Created new project",
        )

        # Log an AI agent action
        await audit_logger.log_ai_action(
            tenant_id=tenant_id,
            agent_type="fire_safety",
            action="analyze_document",
            resource_type="document",
            resource_id=document_id,
            ai_metadata={
                "model": "claude-3-5-sonnet",
                "confidence_score": 0.89,
                "tokens_used": 5420,
            }
        )
    """

    def __init__(self, batch_size: int = 10, flush_interval: int = 5):
        """
        Initialize audit logger.

        Args:
            batch_size: Number of events to accumulate before writing
            flush_interval: Seconds between automatic flushes
        """
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._event_queue: List[AuditEvent] = []
        self._flush_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def start(self):
        """Start the background flush task."""
        if self._flush_task is None:
            self._flush_task = asyncio.create_task(self._periodic_flush())
            logger.info("Audit logger background flush task started")

    async def stop(self):
        """Stop the background flush task and flush remaining events."""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
            self._flush_task = None

        # Flush any remaining events
        await self.flush()
        logger.info("Audit logger stopped")

    async def _periodic_flush(self):
        """Periodically flush events to database."""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic flush: {e}")

    async def flush(self):
        """Flush queued events to database."""
        async with self._lock:
            if not self._event_queue:
                return

            events_to_write = self._event_queue.copy()
            self._event_queue.clear()

        # Write to database
        try:
            async with async_session() as db:
                db.add_all(events_to_write)
                await db.commit()
                logger.debug(f"Flushed {len(events_to_write)} audit events to database")
        except Exception as e:
            logger.error(f"Failed to flush audit events: {e}")
            # Re-add events to queue for retry
            async with self._lock:
                self._event_queue.extend(events_to_write)

    async def _queue_event(self, event: AuditEvent):
        """Add event to queue and flush if batch size reached."""
        async with self._lock:
            self._event_queue.append(event)
            should_flush = len(self._event_queue) >= self.batch_size

        if should_flush:
            await self.flush()

    async def log_event(
        self,
        tenant_id: uuid.UUID,
        event_type: EventType,
        action: str,
        actor_type: str,
        actor_id: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        status: str = "success",
        description: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        ai_metadata: Optional[Dict[str, Any]] = None,
        immediate: bool = False,
    ) -> AuditEvent:
        """
        Log a generic audit event.

        Args:
            tenant_id: Tenant UUID
            event_type: Type of event (from EventType enum)
            action: Action performed (e.g., "login", "upload", "analyze")
            actor_type: Type of actor ("user", "ai_agent", "system")
            actor_id: ID of actor (user_id or agent name)
            user_id: User UUID (if applicable)
            status: Status of action ("success", "failure", "pending")
            description: Human-readable description
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            ip_address: IP address of request
            user_agent: User agent string
            ai_metadata: AI-specific metadata (for AI events)
            immediate: If True, write immediately instead of batching

        Returns:
            Created AuditEvent instance
        """
        event = AuditEvent(
            tenant_id=tenant_id,
            user_id=user_id,
            event_type=event_type,
            action=action,
            status=status,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            actor_type=actor_type,
            actor_id=actor_id,
            ip_address=ip_address,
            user_agent=user_agent,
            ai_metadata=ai_metadata,
        )

        if immediate:
            # Write immediately
            async with async_session() as db:
                db.add(event)
                await db.commit()
                await db.refresh(event)
        else:
            # Queue for batch writing
            await self._queue_event(event)

        return event

    async def log_user_action(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        action: str,
        event_type: EventType = EventType.USER_ACTION,
        status: str = "success",
        description: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditEvent:
        """
        Log a user action.

        Args:
            tenant_id: Tenant UUID
            user_id: User UUID
            action: Action performed
            event_type: Type of event (defaults to USER_ACTION)
            status: Status of action
            description: Description of action
            resource_type: Type of resource (project, document, etc.)
            resource_id: ID of resource
            ip_address: User's IP address
            user_agent: User's user agent

        Returns:
            Created AuditEvent instance
        """
        return await self.log_event(
            tenant_id=tenant_id,
            event_type=event_type,
            action=action,
            actor_type="user",
            actor_id=str(user_id),
            user_id=user_id,
            status=status,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def log_ai_action(
        self,
        tenant_id: uuid.UUID,
        agent_type: str,
        action: str,
        event_type: EventType = EventType.AI_AGENT,
        status: str = "success",
        description: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[uuid.UUID] = None,
        ai_metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> AuditEvent:
        """
        Log an AI agent action.

        Args:
            tenant_id: Tenant UUID
            agent_type: Type of AI agent (fire_safety, structural, etc.)
            action: Action performed
            event_type: Type of event (defaults to AI_AGENT)
            status: Status of action
            description: Description of action
            resource_type: Type of resource
            resource_id: ID of resource
            ai_metadata: AI-specific metadata (model, tokens, confidence, etc.)
            user_id: User who triggered the AI action (if applicable)

        Returns:
            Created AuditEvent instance
        """
        return await self.log_event(
            tenant_id=tenant_id,
            event_type=event_type,
            action=action,
            actor_type="ai_agent",
            actor_id=agent_type,
            user_id=user_id,
            status=status,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            ai_metadata=ai_metadata,
        )

    async def log_system_event(
        self,
        action: str,
        tenant_id: Optional[uuid.UUID] = None,
        status: str = "success",
        description: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[uuid.UUID] = None,
    ) -> AuditEvent:
        """
        Log a system event.

        Args:
            action: Action performed
            tenant_id: Tenant UUID (if applicable)
            status: Status of action
            description: Description of action
            resource_type: Type of resource
            resource_id: ID of resource

        Returns:
            Created AuditEvent instance
        """
        # Use a default tenant_id for system-wide events
        if tenant_id is None:
            tenant_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

        return await self.log_event(
            tenant_id=tenant_id,
            event_type=EventType.SYSTEM,
            action=action,
            actor_type="system",
            actor_id="system",
            status=status,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            immediate=True,  # System events are written immediately
        )

    async def get_recent_events(
        self,
        tenant_id: uuid.UUID,
        limit: int = 50,
        event_type: Optional[EventType] = None,
        actor_type: Optional[str] = None,
        resource_id: Optional[uuid.UUID] = None,
    ) -> List[AuditEvent]:
        """
        Get recent audit events for a tenant.

        Args:
            tenant_id: Tenant UUID
            limit: Maximum number of events to return
            event_type: Filter by event type
            actor_type: Filter by actor type
            resource_id: Filter by resource ID

        Returns:
            List of AuditEvent instances
        """
        async with async_session() as db:
            query = select(AuditEvent).where(AuditEvent.tenant_id == tenant_id)

            if event_type:
                query = query.where(AuditEvent.event_type == event_type)
            if actor_type:
                query = query.where(AuditEvent.actor_type == actor_type)
            if resource_id:
                query = query.where(AuditEvent.resource_id == resource_id)

            query = query.order_by(AuditEvent.timestamp.desc()).limit(limit)

            result = await db.execute(query)
            return result.scalars().all()


# Singleton instance
audit_logger = AuditLogger(batch_size=10, flush_interval=5)


@asynccontextmanager
async def audit_context():
    """
    Context manager for audit logger lifecycle.

    Usage in FastAPI lifespan:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            async with audit_context():
                yield
    """
    await audit_logger.start()
    try:
        yield audit_logger
    finally:
        await audit_logger.stop()

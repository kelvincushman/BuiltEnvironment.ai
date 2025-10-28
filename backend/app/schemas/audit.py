"""
Pydantic schemas for audit endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from ..models.audit import EventType


class AuditEventBase(BaseModel):
    """Base audit event schema."""

    event_type: EventType
    action: str
    status: str
    description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    actor_type: str
    actor_id: Optional[str] = None


class AuditEvent(AuditEventBase):
    """Audit event response schema."""

    id: UUID
    tenant_id: UUID
    user_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditEventList(BaseModel):
    """Paginated list of audit events."""

    events: List[AuditEvent]
    total: int
    skip: int
    limit: int

    @property
    def has_more(self) -> bool:
        """Check if there are more events to load."""
        return (self.skip + self.limit) < self.total


class AuditStatistics(BaseModel):
    """Audit statistics for a time period."""

    total_events: int
    events_by_type: Dict[str, int]
    events_by_status: Dict[str, int]
    events_by_actor: Dict[str, int]
    period_days: int
    start_date: datetime
    end_date: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "total_events": 1523,
                "events_by_type": {
                    "user.action": 892,
                    "ai.agent": 421,
                    "document.upload": 156,
                    "user.auth": 54,
                },
                "events_by_status": {
                    "success": 1498,
                    "error": 22,
                    "failure": 3,
                },
                "events_by_actor": {
                    "user": 1102,
                    "ai_agent": 421,
                },
                "period_days": 30,
                "start_date": "2025-09-28T00:00:00Z",
                "end_date": "2025-10-28T00:00:00Z",
            }
        }


class AuditFilter(BaseModel):
    """Filters for audit event queries."""

    event_type: Optional[EventType] = None
    actor_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[UUID] = None

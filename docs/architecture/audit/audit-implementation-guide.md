# Audit System Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing the comprehensive audit system for BuiltEnvironment.ai.

---

## Implementation Phases

### Phase 1: Core Infrastructure (Weeks 1-2)

#### 1.1 Database Setup

**TimescaleDB Installation**

```bash
# Install TimescaleDB (PostgreSQL extension for time-series data)
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install timescaledb-postgresql-14

# Initialize TimescaleDB
sudo timescaledb-tune --quiet --yes
sudo systemctl restart postgresql
```

**Create Audit Database Schema**

```sql
-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create audit events table
CREATE TABLE audit_events (
    audit_id UUID PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    timestamp_ms BIGINT NOT NULL,

    -- Actor (who performed the action)
    actor_type VARCHAR(20),
    actor_id VARCHAR(100),
    actor_name VARCHAR(200),
    actor_ip_address INET,
    actor_user_agent TEXT,
    actor_session_id VARCHAR(100),

    -- Target (what was acted upon)
    target_type VARCHAR(50),
    target_id VARCHAR(100),
    target_name VARCHAR(200),
    target_metadata JSONB,

    -- Action details
    action_verb VARCHAR(20),
    action_description TEXT,
    action_status VARCHAR(20),
    action_error TEXT,

    -- Context
    context_tenant_id VARCHAR(100),
    context_project_id VARCHAR(100),
    context_request_id VARCHAR(100),
    context_parent_audit_id UUID,

    -- Data changes
    data_before JSONB,
    data_after JSONB,
    data_changes TEXT[],
    data_metadata JSONB,

    -- AI-specific fields
    ai_agent_type VARCHAR(50),
    ai_model VARCHAR(50),
    ai_prompt_tokens INTEGER,
    ai_completion_tokens INTEGER,
    ai_confidence_score DECIMAL(5,4),
    ai_reasoning TEXT,
    ai_tools_used TEXT[],
    ai_execution_time_ms INTEGER,

    -- Compliance fields
    compliance_regulations_checked TEXT[],
    compliance_traffic_light VARCHAR(10),
    compliance_issues_found INTEGER,
    compliance_critical_issues INTEGER,
    compliance_findings JSONB,

    -- Security fields
    security_encryption_used BOOLEAN,
    security_data_classification VARCHAR(20),
    security_retention_period_days INTEGER,
    security_pii_detected BOOLEAN,

    -- Performance metrics
    performance_response_time_ms INTEGER,
    performance_db_query_time_ms INTEGER,
    performance_external_api_time_ms INTEGER,
    performance_memory_used_mb INTEGER,

    -- Indexes
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('audit_events', 'timestamp');

-- Create indexes
CREATE INDEX idx_audit_events_event_type ON audit_events(event_type);
CREATE INDEX idx_audit_events_actor_id ON audit_events(actor_id);
CREATE INDEX idx_audit_events_target_id ON audit_events(target_id);
CREATE INDEX idx_audit_events_tenant_id ON audit_events(context_tenant_id);
CREATE INDEX idx_audit_events_project_id ON audit_events(context_project_id);
CREATE INDEX idx_audit_events_request_id ON audit_events(context_request_id);
CREATE INDEX idx_audit_events_timestamp ON audit_events(timestamp DESC);

-- GIN index for JSONB fields
CREATE INDEX idx_audit_events_target_metadata ON audit_events USING GIN(target_metadata);
CREATE INDEX idx_audit_events_data_metadata ON audit_events USING GIN(data_metadata);
CREATE INDEX idx_audit_events_compliance_findings ON audit_events USING GIN(compliance_findings);

-- Composite indexes for common queries
CREATE INDEX idx_audit_events_actor_timestamp ON audit_events(actor_id, timestamp DESC);
CREATE INDEX idx_audit_events_tenant_timestamp ON audit_events(context_tenant_id, timestamp DESC);
CREATE INDEX idx_audit_events_ai_type_timestamp ON audit_events(ai_agent_type, timestamp DESC);

-- Compression policy (compress data older than 7 days)
SELECT add_compression_policy('audit_events', INTERVAL '7 days');

-- Retention policy (drop data older than 7 years for most events)
SELECT add_retention_policy('audit_events', INTERVAL '7 years');
```

**Elasticsearch Setup**

```bash
# Install Elasticsearch 8.x
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt-get update && sudo apt-get install elasticsearch

# Start Elasticsearch
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch
```

**Create Elasticsearch Index**

```json
PUT /audit_events
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "index": {
      "lifecycle": {
        "name": "audit_policy",
        "rollover_alias": "audit_events"
      }
    }
  },
  "mappings": {
    "properties": {
      "audit_id": { "type": "keyword" },
      "event_type": { "type": "keyword" },
      "timestamp": { "type": "date" },
      "actor": {
        "properties": {
          "type": { "type": "keyword" },
          "id": { "type": "keyword" },
          "name": { "type": "text" },
          "ip_address": { "type": "ip" },
          "user_agent": { "type": "text" },
          "session_id": { "type": "keyword" }
        }
      },
      "target": {
        "properties": {
          "type": { "type": "keyword" },
          "id": { "type": "keyword" },
          "name": { "type": "text" },
          "metadata": { "type": "object", "enabled": true }
        }
      },
      "action": {
        "properties": {
          "verb": { "type": "keyword" },
          "description": { "type": "text" },
          "status": { "type": "keyword" },
          "error": { "type": "text" }
        }
      },
      "context": {
        "properties": {
          "tenant_id": { "type": "keyword" },
          "project_id": { "type": "keyword" },
          "request_id": { "type": "keyword" },
          "parent_audit_id": { "type": "keyword" }
        }
      },
      "ai_specific": {
        "properties": {
          "agent_type": { "type": "keyword" },
          "model": { "type": "keyword" },
          "confidence_score": { "type": "float" },
          "reasoning": { "type": "text" },
          "tools_used": { "type": "keyword" }
        }
      },
      "compliance": {
        "properties": {
          "regulations_checked": { "type": "keyword" },
          "traffic_light_status": { "type": "keyword" },
          "issues_found": { "type": "integer" },
          "findings": { "type": "object", "enabled": true }
        }
      }
    }
  }
}
```

#### 1.2 Audit Logger Implementation

**Core Audit Logger Class**

```python
# audit_logger.py

import asyncio
import asyncpg
from elasticsearch import AsyncElasticsearch
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import json
from collections import deque
import aioredis

class AuditLogger:
    """Central audit logging system"""

    def __init__(
        self,
        pg_connection_string: str,
        elasticsearch_url: str,
        redis_url: str,
        batch_size: int = 100,
        batch_interval: float = 5.0
    ):
        self.pg_connection_string = pg_connection_string
        self.elasticsearch_url = elasticsearch_url
        self.redis_url = redis_url
        self.batch_size = batch_size
        self.batch_interval = batch_interval

        # Batch buffer
        self.event_buffer: deque = deque()
        self.buffer_lock = asyncio.Lock()

        # Connections (initialized in start())
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.es_client: Optional[AsyncElasticsearch] = None
        self.redis_client: Optional[aioredis.Redis] = None

        # Background task
        self.batch_task: Optional[asyncio.Task] = None
        self.running = False

    async def start(self):
        """Initialize connections and start background processing"""

        # PostgreSQL connection pool
        self.pg_pool = await asyncpg.create_pool(
            self.pg_connection_string,
            min_size=5,
            max_size=20
        )

        # Elasticsearch client
        self.es_client = AsyncElasticsearch([self.elasticsearch_url])

        # Redis for distributed locking and caching
        self.redis_client = await aioredis.from_url(self.redis_url)

        # Start background batch processor
        self.running = True
        self.batch_task = asyncio.create_task(self._batch_processor())

        print("AuditLogger started")

    async def stop(self):
        """Gracefully shutdown and flush remaining events"""

        self.running = False

        # Wait for batch processor to finish
        if self.batch_task:
            await self.batch_task

        # Flush remaining events
        await self._flush_buffer()

        # Close connections
        if self.pg_pool:
            await self.pg_pool.close()
        if self.es_client:
            await self.es_client.close()
        if self.redis_client:
            await self.redis_client.close()

        print("AuditLogger stopped")

    async def log_event(self, event: Dict) -> str:
        """Log an audit event (async, non-blocking)"""

        # Ensure audit_id exists
        if "audit_id" not in event:
            event["audit_id"] = str(uuid.uuid4())

        # Ensure timestamp exists
        if "timestamp" not in event:
            event["timestamp"] = datetime.utcnow().isoformat()

        # Add to buffer
        async with self.buffer_lock:
            self.event_buffer.append(event)

            # If buffer is full, flush immediately
            if len(self.event_buffer) >= self.batch_size:
                await self._flush_buffer()

        return event["audit_id"]

    async def log_event_sync(self, event: Dict) -> str:
        """Log an audit event synchronously (blocks until written)"""

        audit_id = await self.log_event(event)

        # Force flush
        await self._flush_buffer()

        return audit_id

    async def _batch_processor(self):
        """Background task to periodically flush buffer"""

        while self.running:
            await asyncio.sleep(self.batch_interval)

            async with self.buffer_lock:
                if len(self.event_buffer) > 0:
                    await self._flush_buffer()

    async def _flush_buffer(self):
        """Flush buffered events to databases"""

        if len(self.event_buffer) == 0:
            return

        # Get events from buffer
        events = []
        while self.event_buffer:
            events.append(self.event_buffer.popleft())

        try:
            # Write to TimescaleDB (primary storage)
            await self._write_to_timescale(events)

            # Write to Elasticsearch (search index)
            await self._write_to_elasticsearch(events)

            # Update Redis cache (recent events)
            await self._update_redis_cache(events)

            print(f"Flushed {len(events)} audit events")

        except Exception as e:
            print(f"Error flushing audit events: {e}")

            # Re-add events to buffer for retry
            self.event_buffer.extendleft(reversed(events))
            raise

    async def _write_to_timescale(self, events: List[Dict]):
        """Write events to TimescaleDB"""

        query = """
        INSERT INTO audit_events (
            audit_id, event_type, timestamp, timestamp_ms,
            actor_type, actor_id, actor_name, actor_ip_address, actor_user_agent, actor_session_id,
            target_type, target_id, target_name, target_metadata,
            action_verb, action_description, action_status, action_error,
            context_tenant_id, context_project_id, context_request_id, context_parent_audit_id,
            data_before, data_after, data_changes, data_metadata,
            ai_agent_type, ai_model, ai_prompt_tokens, ai_completion_tokens,
            ai_confidence_score, ai_reasoning, ai_tools_used, ai_execution_time_ms,
            compliance_regulations_checked, compliance_traffic_light,
            compliance_issues_found, compliance_critical_issues, compliance_findings,
            security_encryption_used, security_data_classification,
            security_retention_period_days, security_pii_detected,
            performance_response_time_ms, performance_db_query_time_ms,
            performance_external_api_time_ms, performance_memory_used_mb
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
            $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
            $21, $22, $23, $24, $25, $26, $27, $28, $29, $30,
            $31, $32, $33, $34, $35, $36, $37, $38, $39, $40,
            $41, $42, $43, $44, $45, $46, $47, $48
        )
        """

        async with self.pg_pool.acquire() as conn:
            # Use executemany for batch insert
            await conn.executemany(
                query,
                [self._event_to_tuple(event) for event in events]
            )

    def _event_to_tuple(self, event: Dict) -> tuple:
        """Convert event dict to tuple for database insert"""

        actor = event.get("actor", {})
        target = event.get("target", {})
        action = event.get("action", {})
        context = event.get("context", {})
        data = event.get("data", {})
        ai = event.get("ai_specific", {})
        compliance = event.get("compliance", {})
        security = event.get("security", {})
        performance = event.get("performance", {})

        timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))

        return (
            uuid.UUID(event["audit_id"]),
            event["event_type"],
            timestamp,
            int(timestamp.timestamp() * 1000),
            actor.get("type"),
            actor.get("id"),
            actor.get("name"),
            actor.get("ip_address"),
            actor.get("user_agent"),
            actor.get("session_id"),
            target.get("type"),
            target.get("id"),
            target.get("name"),
            json.dumps(target.get("metadata")) if target.get("metadata") else None,
            action.get("verb"),
            action.get("description"),
            action.get("status"),
            action.get("error"),
            context.get("tenant_id"),
            context.get("project_id"),
            context.get("request_id"),
            uuid.UUID(context["parent_audit_id"]) if context.get("parent_audit_id") else None,
            json.dumps(data.get("before")) if data.get("before") else None,
            json.dumps(data.get("after")) if data.get("after") else None,
            data.get("changes"),
            json.dumps(data.get("metadata")) if data.get("metadata") else None,
            ai.get("agent_type"),
            ai.get("model"),
            ai.get("prompt_tokens"),
            ai.get("completion_tokens"),
            ai.get("confidence_score"),
            ai.get("reasoning"),
            ai.get("tools_used"),
            ai.get("execution_time_ms"),
            compliance.get("regulations_checked"),
            compliance.get("traffic_light_status"),
            compliance.get("issues_found"),
            compliance.get("critical_issues"),
            json.dumps(compliance.get("findings")) if compliance.get("findings") else None,
            security.get("encryption_used"),
            security.get("data_classification"),
            security.get("retention_period_days"),
            security.get("pii_detected"),
            performance.get("response_time_ms"),
            performance.get("database_query_time_ms"),
            performance.get("external_api_time_ms"),
            performance.get("memory_used_mb")
        )

    async def _write_to_elasticsearch(self, events: List[Dict]):
        """Write events to Elasticsearch for search"""

        operations = []
        for event in events:
            # Index operation
            operations.append({"index": {"_index": "audit_events", "_id": event["audit_id"]}})
            # Document
            operations.append(event)

        # Bulk insert
        await self.es_client.bulk(operations=operations)

    async def _update_redis_cache(self, events: List[Dict]):
        """Update Redis cache with recent events"""

        # Cache recent events per user for quick access
        for event in events:
            actor_id = event.get("actor", {}).get("id")
            if actor_id:
                # Add to user's recent activity (keep last 100)
                cache_key = f"audit:recent:{actor_id}"
                await self.redis_client.lpush(cache_key, json.dumps(event))
                await self.redis_client.ltrim(cache_key, 0, 99)
                await self.redis_client.expire(cache_key, 86400)  # 24 hours

    async def query_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        target_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Query audit events"""

        # Build WHERE clause
        conditions = ["TRUE"]
        params = []
        param_count = 0

        if start_time:
            param_count += 1
            conditions.append(f"timestamp >= ${param_count}")
            params.append(start_time)

        if end_time:
            param_count += 1
            conditions.append(f"timestamp <= ${param_count}")
            params.append(end_time)

        if event_type:
            param_count += 1
            conditions.append(f"event_type = ${param_count}")
            params.append(event_type)

        if actor_id:
            param_count += 1
            conditions.append(f"actor_id = ${param_count}")
            params.append(actor_id)

        if target_id:
            param_count += 1
            conditions.append(f"target_id = ${param_count}")
            params.append(target_id)

        if tenant_id:
            param_count += 1
            conditions.append(f"context_tenant_id = ${param_count}")
            params.append(tenant_id)

        param_count += 1
        params.append(limit)

        query = f"""
        SELECT * FROM audit_events
        WHERE {' AND '.join(conditions)}
        ORDER BY timestamp DESC
        LIMIT ${param_count}
        """

        async with self.pg_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]


# Global audit logger instance
audit_logger: Optional[AuditLogger] = None


async def init_audit_logger():
    """Initialize global audit logger"""
    global audit_logger

    audit_logger = AuditLogger(
        pg_connection_string=os.getenv("AUDIT_DB_URL"),
        elasticsearch_url=os.getenv("ELASTICSEARCH_URL"),
        redis_url=os.getenv("REDIS_URL")
    )

    await audit_logger.start()
    return audit_logger


async def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    if audit_logger is None:
        raise RuntimeError("Audit logger not initialized")
    return audit_logger
```

#### 1.3 FastAPI Integration

**Middleware for Request/Response Auditing**

```python
# middleware/audit_middleware.py

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to audit all HTTP requests"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())

        # Extract user info from request
        user = await self.extract_user(request)

        # Execute request
        response = await call_next(request)

        # Calculate response time
        response_time = (time.time() - start_time) * 1000

        # Log audit event
        audit_logger = await get_audit_logger()
        await audit_logger.log_event({
            "event_type": f"api.{request.method.lower()}.{request.url.path}",
            "timestamp": datetime.utcnow().isoformat(),

            "actor": {
                "type": "user" if user else "anonymous",
                "id": user.get("id") if user else None,
                "name": user.get("name") if user else None,
                "ip_address": request.client.host,
                "user_agent": request.headers.get("user-agent"),
                "session_id": request.cookies.get("session_id")
            },

            "target": {
                "type": "api_endpoint",
                "id": request.url.path,
                "name": f"{request.method} {request.url.path}"
            },

            "action": {
                "verb": request.method,
                "description": f"{request.method} request to {request.url.path}",
                "status": "success" if response.status_code < 400 else "failure"
            },

            "context": {
                "request_id": request_id,
                "tenant_id": user.get("tenant_id") if user else None
            },

            "performance": {
                "response_time_ms": int(response_time)
            }
        })

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response

    async def extract_user(self, request: Request) -> Optional[Dict]:
        """Extract user information from request"""
        # Implementation depends on your auth system
        # This is a placeholder
        if "Authorization" in request.headers:
            # Decode JWT, validate session, etc.
            return {"id": "user-123", "name": "John Doe", "tenant_id": "tenant-789"}
        return None


# Add to FastAPI app
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(AuditMiddleware)
```

---

### Phase 2: AI Integration (Weeks 3-4)

Implement LangGraph and Langflow audit integrations as described in `langgraph-langflow-audit-integration.md`.

---

### Phase 3: Audit UI & Dashboards (Weeks 5-6)

See `audit-dashboard-specifications.md` for detailed UI implementation.

---

### Phase 4: Reporting & Compliance (Weeks 7-8)

Implement compliance reports, GDPR export tools, and retention policies.

---

## Testing Strategy

### Unit Tests

```python
import pytest
from audit_logger import AuditLogger

@pytest.mark.asyncio
async def test_audit_event_logging():
    """Test basic audit event logging"""

    logger = AuditLogger(...)
    await logger.start()

    audit_id = await logger.log_event({
        "event_type": "test.event",
        "actor": {"type": "user", "id": "test-user"},
        "action": {"verb": "test", "status": "success"}
    })

    assert audit_id is not None

    # Query the event
    events = await logger.query_events(actor_id="test-user", limit=1)
    assert len(events) == 1
    assert events[0]["event_type"] == "test.event"

    await logger.stop()
```

### Integration Tests

Test complete workflows with audit trail verification.

### Load Tests

```python
import asyncio
from locust import HttpUser, task, between

class AuditLoadTest(HttpUser):
    wait_time = between(1, 3)

    @task
    def create_audit_events(self):
        """Simulate high-volume audit event creation"""
        for _ in range(100):
            self.client.post("/api/audit/event", json={
                "event_type": "load.test",
                "actor": {"type": "user", "id": "load-test-user"},
                "action": {"verb": "test", "status": "success"}
            })
```

---

## Monitoring & Operations

### Health Checks

```python
@app.get("/health/audit")
async def audit_health_check():
    """Check audit system health"""

    audit_logger = await get_audit_logger()

    # Check TimescaleDB
    pg_healthy = await audit_logger.pg_pool.fetchval("SELECT 1")

    # Check Elasticsearch
    es_healthy = await audit_logger.es_client.ping()

    # Check Redis
    redis_healthy = await audit_logger.redis_client.ping()

    # Check buffer size
    buffer_size = len(audit_logger.event_buffer)

    return {
        "status": "healthy" if all([pg_healthy, es_healthy, redis_healthy]) else "unhealthy",
        "timescaledb": "healthy" if pg_healthy else "unhealthy",
        "elasticsearch": "healthy" if es_healthy else "unhealthy",
        "redis": "healthy" if redis_healthy else "unhealthy",
        "buffer_size": buffer_size,
        "buffer_max_size": audit_logger.batch_size
    }
```

### Metrics

Export Prometheus metrics for monitoring:

```python
from prometheus_client import Counter, Histogram, Gauge

audit_events_total = Counter('audit_events_total', 'Total audit events logged', ['event_type', 'status'])
audit_event_duration = Histogram('audit_event_duration_seconds', 'Time to log audit event')
audit_buffer_size = Gauge('audit_buffer_size', 'Current audit event buffer size')
```

---

## Deployment

### Docker Compose Example

```yaml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg14
    environment:
      POSTGRES_DB: audit
      POSTGRES_USER: audit_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - timescale_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  audit_api:
    build: .
    environment:
      AUDIT_DB_URL: postgresql://audit_user:${DB_PASSWORD}@timescaledb:5432/audit
      ELASTICSEARCH_URL: http://elasticsearch:9200
      REDIS_URL: redis://redis:6379
    depends_on:
      - timescaledb
      - elasticsearch
      - redis
    ports:
      - "8000:8000"

volumes:
  timescale_data:
  es_data:
  redis_data:
```

---

## Summary

This implementation guide provides:

✅ **Complete database schema** for TimescaleDB and Elasticsearch
✅ **Production-ready audit logger** with batching and async processing
✅ **FastAPI middleware** for automatic request/response auditing
✅ **Testing strategy** with unit, integration, and load tests
✅ **Monitoring and health checks** for operational excellence
✅ **Docker deployment** configuration

Follow this guide phase-by-phase to implement a robust, scalable audit system.

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-27

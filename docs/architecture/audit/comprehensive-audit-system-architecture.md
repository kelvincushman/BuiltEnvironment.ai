# Comprehensive Audit System Architecture - BuiltEnvironment.ai

## Overview

This document defines the complete audit logging and tracking system for BuiltEnvironment.ai, ensuring full transparency, compliance, and accountability for all user actions, AI agent operations, and system events.

## Audit System Objectives

### Primary Goals

1. **Complete Traceability**: Track every action, decision, and data change in the system
2. **AI Transparency**: Record all AI agent operations with inputs, outputs, and reasoning
3. **Compliance**: Meet GDPR, ISO 27001, and industry audit requirements
4. **Security**: Enable threat detection and forensic analysis
5. **Accountability**: Establish clear attribution for all system changes
6. **Performance**: Monitor system performance and identify optimization opportunities

### Regulatory Compliance

- **GDPR Article 15**: Right of access - users can retrieve all audit records about their data
- **GDPR Article 17**: Right to erasure - complete audit trail of data deletion
- **ISO 27001**: Information security management system audit requirements
- **ISO 19650**: BIM information management audit trails
- **UK Building Regulations**: Compliance checking audit trails for accountability

---

## Audit System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
│  (User Actions, AI Agents, System Events)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Audit Event Collector                         │
│  - Event normalization                                          │
│  - Schema validation                                            │
│  - Enrichment (timestamps, user context, IP, etc.)             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Audit Event Router                           │
│  - Priority classification                                      │
│  - Real-time vs. batch routing                                 │
│  - Storage destination selection                               │
└────┬────────────────┬────────────────┬──────────────────────────┘
     │                │                │
     ▼                ▼                ▼
┌──────────┐   ┌────────────┐   ┌────────────────┐
│  Time    │   │  Search    │   │    Long-Term   │
│  Series  │   │  Index     │   │    Archive     │
│  DB      │   │  (Elastic) │   │    (S3)        │
│(TimescaleDB)  (Elasticsearch) (Cold Storage)    │
└──────────┘   └────────────┘   └────────────────┘
     │                │                │
     └────────────────┴────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Audit Query API                              │
│  - Search and retrieval                                         │
│  - Aggregation and analytics                                    │
│  - Export and reporting                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Audit UI & Dashboards                        │
│  - Activity timeline                                            │
│  - AI agent trace viewer                                        │
│  - Compliance reports                                           │
│  - Security monitoring                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Audit Event Collector

**Purpose**: Capture all audit events from various sources with standardized format.

**Responsibilities**:
- Receive events from application components
- Normalize event data to standard schema
- Enrich with contextual information
- Validate event structure
- Generate unique audit IDs

**Integration Points**:
- FastAPI middleware (HTTP requests/responses)
- Database triggers (data changes)
- Langflow webhooks (workflow events)
- LangGraph checkpoints (AI agent state)
- Background job system (async operations)

#### 2. Audit Event Router

**Purpose**: Intelligent routing of audit events to appropriate storage systems.

**Routing Rules**:
```
High Priority Events (Security, Compliance) → Real-time → All Stores
Standard Events → Batch (5 min) → Time Series + Search
Low Priority Events (Debug, Info) → Batch (30 min) → Time Series only
Historical Events (>90 days) → Archive → S3 Cold Storage
```

#### 3. Storage Systems

**TimescaleDB (Time Series)**:
- Primary storage for all audit events
- Optimized for time-series queries
- Automatic data retention policies
- Fast aggregation queries

**Elasticsearch (Search Index)**:
- Full-text search across audit logs
- Complex filtering and aggregation
- Near real-time search capability
- Dashboard and visualization support

**S3 Cold Storage (Archive)**:
- Long-term retention (7 years for compliance)
- Compressed and encrypted storage
- Cost-effective for historical data
- Retrievable for compliance audits

#### 4. Audit Query API

**Purpose**: Provide unified interface for audit data retrieval.

**Capabilities**:
- RESTful API for programmatic access
- GraphQL for flexible queries
- WebSocket for real-time event streaming
- Batch export for compliance reporting

---

## Event Categories and Types

### 1. User Activity Events

**Authentication Events**:
- `user.login.success`
- `user.login.failure`
- `user.logout`
- `user.session.expired`
- `user.password.changed`
- `user.mfa.enabled`
- `user.mfa.disabled`

**Document Events**:
- `document.uploaded`
- `document.viewed`
- `document.downloaded`
- `document.edited`
- `document.deleted`
- `document.shared`
- `document.permission.changed`

**Project Events**:
- `project.created`
- `project.updated`
- `project.deleted`
- `project.member.added`
- `project.member.removed`
- `project.role.changed`

### 2. AI Agent Events

**Langflow Workflow Events**:
- `workflow.started`
- `workflow.node.executed`
- `workflow.completed`
- `workflow.failed`
- `workflow.timeout`

**LangGraph Agent Events**:
- `agent.invoked`
- `agent.tool.called`
- `agent.state.updated`
- `agent.decision.made`
- `agent.checkpoint.created`
- `agent.rollback.performed`

**AI Analysis Events**:
- `analysis.compliance.started`
- `analysis.compliance.completed`
- `analysis.standard.checked`
- `analysis.conflict.detected`
- `analysis.recommendation.generated`

**Specialized Agent Events**:
- `agent.structural.analysis`
- `agent.mep.validation`
- `agent.fire_safety.assessment`
- `agent.accessibility.check`
- `agent.energy.calculation`

### 3. Data Events

**Database Operations**:
- `data.record.created`
- `data.record.updated`
- `data.record.deleted`
- `data.bulk.import`
- `data.bulk.export`

**RAG Database Events**:
- `rag.document.indexed`
- `rag.document.updated`
- `rag.query.executed`
- `rag.chunk.retrieved`
- `rag.embedding.generated`

**Data Protection Events**:
- `data.encrypted`
- `data.decrypted`
- `data.anonymized`
- `data.purged`
- `data.retention.policy.applied`

### 4. Compliance Events

**Regulation Checking**:
- `compliance.check.initiated`
- `compliance.part_a.validated` (for each Part A-S)
- `compliance.traffic_light.assigned`
- `compliance.issue.identified`
- `compliance.report.generated`

**Standards Validation**:
- `standards.bs_7671.checked`
- `standards.iso_19650.validated`
- `standards.cibse.verified`
- `standards.performance.assessed`

### 5. System Events

**Infrastructure Events**:
- `system.startup`
- `system.shutdown`
- `system.error`
- `system.health_check.failed`
- `system.backup.completed`

**Performance Events**:
- `performance.slow_query`
- `performance.high_memory`
- `performance.rate_limit.exceeded`

**Security Events**:
- `security.unauthorized_access`
- `security.suspicious_activity`
- `security.api_key.compromised`
- `security.encryption.failure`

---

## Audit Event Schema

### Standard Event Structure

```json
{
  "audit_id": "uuid-v4",
  "event_type": "string (category.subcategory.action)",
  "timestamp": "ISO 8601 timestamp",
  "timestamp_ms": "Unix timestamp in milliseconds",

  "actor": {
    "type": "user|agent|system",
    "id": "uuid or system identifier",
    "name": "human readable name",
    "ip_address": "IPv4/IPv6",
    "user_agent": "browser/client info",
    "session_id": "session identifier"
  },

  "target": {
    "type": "document|project|user|workflow",
    "id": "target resource ID",
    "name": "resource name",
    "metadata": {}
  },

  "action": {
    "verb": "create|read|update|delete|execute",
    "description": "human readable description",
    "status": "success|failure|partial",
    "error": "error message if failed"
  },

  "context": {
    "tenant_id": "multi-tenant identifier",
    "project_id": "project context",
    "request_id": "request trace ID",
    "parent_audit_id": "related audit event ID"
  },

  "data": {
    "before": "state before action (for updates)",
    "after": "state after action",
    "changes": ["list of changed fields"],
    "metadata": {}
  },

  "ai_specific": {
    "agent_type": "structural|mep|fire_safety|etc",
    "model": "claude-3-opus|sonnet|etc",
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "confidence_score": 0.95,
    "reasoning": "AI reasoning trace",
    "tools_used": ["list of tools"],
    "execution_time_ms": 0
  },

  "compliance": {
    "regulations_checked": ["Part A", "Part B", "ISO 19650"],
    "traffic_light_status": "green|amber|red",
    "issues_found": 0,
    "critical_issues": 0
  },

  "security": {
    "encryption_used": true,
    "data_classification": "public|internal|confidential|restricted",
    "retention_period_days": 365,
    "pii_detected": false
  },

  "performance": {
    "response_time_ms": 0,
    "database_query_time_ms": 0,
    "external_api_time_ms": 0,
    "memory_used_mb": 0
  }
}
```

### Example: User Document Upload Event

```json
{
  "audit_id": "550e8400-e29b-41d4-a716-446655440001",
  "event_type": "document.uploaded",
  "timestamp": "2025-10-27T14:30:00.123Z",
  "timestamp_ms": 1730040600123,

  "actor": {
    "type": "user",
    "id": "user-123",
    "name": "John Smith",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "session_id": "session-abc-123"
  },

  "target": {
    "type": "document",
    "id": "doc-456",
    "name": "MEP_Specifications_Rev_C.pdf",
    "metadata": {
      "file_size": 2457600,
      "mime_type": "application/pdf",
      "pages": 45
    }
  },

  "action": {
    "verb": "create",
    "description": "User uploaded MEP specifications document",
    "status": "success"
  },

  "context": {
    "tenant_id": "tenant-789",
    "project_id": "project-101",
    "request_id": "req-xyz-999"
  },

  "data": {
    "after": {
      "document_id": "doc-456",
      "status": "uploaded",
      "revision": "C",
      "discipline": "MEP"
    },
    "metadata": {
      "original_filename": "MEP_Specifications_Rev_C.pdf",
      "uploaded_via": "web_ui"
    }
  },

  "security": {
    "encryption_used": true,
    "data_classification": "confidential",
    "retention_period_days": 2555,
    "pii_detected": false
  },

  "performance": {
    "response_time_ms": 450,
    "database_query_time_ms": 25,
    "file_upload_time_ms": 400
  }
}
```

### Example: AI Agent Compliance Check Event

```json
{
  "audit_id": "650e8400-e29b-41d4-a716-446655440002",
  "event_type": "agent.compliance.completed",
  "timestamp": "2025-10-27T14:35:22.456Z",
  "timestamp_ms": 1730040922456,

  "actor": {
    "type": "agent",
    "id": "agent-fire-safety-01",
    "name": "Fire Safety Compliance Agent",
    "session_id": "agent-session-def-456"
  },

  "target": {
    "type": "document",
    "id": "doc-456",
    "name": "MEP_Specifications_Rev_C.pdf"
  },

  "action": {
    "verb": "execute",
    "description": "Fire safety compliance analysis completed",
    "status": "success"
  },

  "context": {
    "tenant_id": "tenant-789",
    "project_id": "project-101",
    "request_id": "req-xyz-999",
    "parent_audit_id": "550e8400-e29b-41d4-a716-446655440001"
  },

  "data": {
    "after": {
      "analysis_id": "analysis-789",
      "status": "completed",
      "findings_count": 5
    }
  },

  "ai_specific": {
    "agent_type": "fire_safety",
    "model": "claude-sonnet-4",
    "prompt_tokens": 12500,
    "completion_tokens": 3200,
    "confidence_score": 0.92,
    "reasoning": "Analyzed fire detection systems, escape routes, compartmentation, and suppression systems. Identified 3 green items, 2 amber requiring clarification.",
    "tools_used": ["document_processor", "regulation_checker", "standards_validator"],
    "execution_time_ms": 45000
  },

  "compliance": {
    "regulations_checked": ["Part B", "BS 9999", "BS EN 12845"],
    "traffic_light_status": "amber",
    "issues_found": 2,
    "critical_issues": 0,
    "findings": [
      {
        "regulation": "Part B.2",
        "status": "amber",
        "issue": "Fire alarm system coverage needs verification in plant rooms"
      },
      {
        "regulation": "BS 9999 Section 18",
        "status": "amber",
        "issue": "Emergency lighting lux levels not explicitly stated"
      }
    ]
  },

  "performance": {
    "response_time_ms": 45000,
    "database_query_time_ms": 200,
    "external_api_time_ms": 42000,
    "memory_used_mb": 512
  }
}
```

---

## Data Retention and Lifecycle

### Retention Policies

```
┌─────────────────────┬──────────────┬────────────────┬──────────────┐
│ Event Category      │ Hot Storage  │ Warm Storage   │ Cold Archive │
├─────────────────────┼──────────────┼────────────────┼──────────────┤
│ Security Events     │ 90 days      │ 2 years        │ 7 years      │
│ Compliance Events   │ 90 days      │ 2 years        │ 7 years      │
│ User Activity       │ 30 days      │ 1 year         │ 3 years      │
│ AI Agent Events     │ 30 days      │ 1 year         │ 3 years      │
│ System Events       │ 14 days      │ 90 days        │ 1 year       │
│ Performance Events  │ 7 days       │ 30 days        │ 90 days      │
└─────────────────────┴──────────────┴────────────────┴──────────────┘
```

### Storage Tiers

**Hot Storage (TimescaleDB + Elasticsearch)**:
- Fast queries (< 100ms)
- Full search capabilities
- Real-time analytics
- Highest cost per GB

**Warm Storage (TimescaleDB Compressed)**:
- Medium query speed (< 1s)
- Limited search (time-based only)
- Aggregated analytics
- Medium cost per GB

**Cold Storage (S3 Glacier)**:
- Slow retrieval (minutes to hours)
- Compliance/audit access only
- Compressed and encrypted
- Lowest cost per GB

### Lifecycle Automation

```python
# Pseudo-code for automated lifecycle management
def manage_audit_lifecycle():
    # Move to warm storage
    events_30_days_old = query_events(age_days=30)
    compress_and_move(events_30_days_old, destination="warm_storage")

    # Move to cold archive
    events_90_days_old = query_events(age_days=90)
    archive_to_s3(events_90_days_old, bucket="audit-cold-archive")

    # Delete after retention period
    events_past_retention = query_events_past_retention()
    for event in events_past_retention:
        if user_has_right_to_erasure(event.user_id):
            permanently_delete(event)
        else:
            archive_for_compliance(event, years=7)
```

---

## Query and Reporting

### Common Query Patterns

**1. User Activity Timeline**
```sql
SELECT timestamp, event_type, action.description, target.name
FROM audit_events
WHERE actor.id = 'user-123'
  AND timestamp > NOW() - INTERVAL '30 days'
ORDER BY timestamp DESC
LIMIT 100;
```

**2. AI Agent Performance Analysis**
```sql
SELECT
  ai_specific.agent_type,
  COUNT(*) as total_executions,
  AVG(performance.response_time_ms) as avg_response_time,
  AVG(ai_specific.confidence_score) as avg_confidence,
  SUM(ai_specific.prompt_tokens + ai_specific.completion_tokens) as total_tokens
FROM audit_events
WHERE event_type LIKE 'agent.%'
  AND timestamp > NOW() - INTERVAL '7 days'
GROUP BY ai_specific.agent_type;
```

**3. Compliance Issues Trend**
```sql
SELECT
  DATE_TRUNC('day', timestamp) as day,
  compliance.traffic_light_status,
  COUNT(*) as count
FROM audit_events
WHERE event_type = 'compliance.check.completed'
  AND timestamp > NOW() - INTERVAL '90 days'
GROUP BY day, compliance.traffic_light_status
ORDER BY day;
```

**4. Security Event Monitoring**
```sql
SELECT timestamp, event_type, actor.ip_address, action.description
FROM audit_events
WHERE event_type LIKE 'security.%'
  OR action.status = 'failure'
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

### Pre-Built Reports

1. **Daily Activity Summary**
2. **AI Agent Performance Report**
3. **Compliance Check Results**
4. **Security Incident Report**
5. **User Access Report (GDPR)**
6. **System Health Report**
7. **Cost Analysis (Token Usage)**

---

## Integration Points

### 1. LangGraph Integration

**Checkpoint Auditing**:
```python
from langgraph.checkpoint import MemorySaver

async def audit_checkpoint(checkpoint_data):
    """Audit LangGraph checkpoint creation"""
    await create_audit_event({
        "event_type": "agent.checkpoint.created",
        "ai_specific": {
            "agent_type": checkpoint_data.agent_type,
            "state": checkpoint_data.state,
            "node": checkpoint_data.current_node
        }
    })

# Configure LangGraph with audit callback
checkpointer = MemorySaver(on_checkpoint=audit_checkpoint)
```

### 2. Langflow Integration

**Workflow Event Webhooks**:
```yaml
# Langflow configuration
webhooks:
  - event: "workflow.started"
    url: "https://api.builtenvironment.ai/audit/webhook"
    headers:
      Authorization: "Bearer ${AUDIT_API_KEY}"

  - event: "workflow.node.executed"
    url: "https://api.builtenvironment.ai/audit/webhook"

  - event: "workflow.completed"
    url: "https://api.builtenvironment.ai/audit/webhook"
```

### 3. FastAPI Middleware

```python
from fastapi import Request
from audit_logger import AuditLogger

@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    """Audit all HTTP requests"""
    start_time = time.time()

    # Execute request
    response = await call_next(request)

    # Log audit event
    await AuditLogger.log({
        "event_type": f"api.{request.method.lower()}.{request.url.path}",
        "actor": extract_user(request),
        "action": {
            "verb": request.method,
            "status": "success" if response.status_code < 400 else "failure"
        },
        "performance": {
            "response_time_ms": (time.time() - start_time) * 1000
        }
    })

    return response
```

---

## Security and Privacy

### Access Control

**Audit Log Access Levels**:
- **System Administrators**: Full access to all audit logs
- **Security Officers**: Access to security and compliance events
- **Project Managers**: Access to their project's events only
- **Users**: Access to their own activity logs (GDPR right to access)
- **Auditors**: Read-only access with export capability

### Data Protection

**Sensitive Data Handling**:
- PII (Personally Identifiable Information) is hashed or tokenized
- Document content is NOT stored in audit logs (only metadata)
- Passwords and API keys are NEVER logged
- Credit card numbers and financial data are redacted

**Audit Log Integrity**:
- Audit events are immutable (append-only)
- Cryptographic signatures for tamper detection
- Regular integrity verification
- Blockchain anchoring for high-security use cases (optional)

---

## Monitoring and Alerts

### Real-Time Alerts

**Security Alerts**:
- Multiple failed login attempts
- Unauthorized access attempts
- Suspicious activity patterns
- Data exfiltration indicators

**Operational Alerts**:
- AI agent failures or timeouts
- Compliance check failures
- System performance degradation
- Data retention policy violations

**Business Alerts**:
- High token usage (cost control)
- Low AI confidence scores
- SLA violations
- User experience issues

### Alert Destinations

- Email notifications
- Slack/Teams webhooks
- PagerDuty for critical issues
- Dashboard notifications
- SMS for security incidents

---

## Next Steps

1. Implement audit event collector and router
2. Set up TimescaleDB and Elasticsearch
3. Integrate with LangGraph and Langflow
4. Develop audit query API
5. Build audit dashboard UI
6. Implement retention policies
7. Create compliance reports
8. Set up monitoring and alerting

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-27
**Owner**: BuiltEnvironment.ai Architecture Team

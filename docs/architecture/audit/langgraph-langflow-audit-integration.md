# LangGraph & Langflow Audit Integration Guide

## Overview

This document provides comprehensive guidance for integrating audit logging with LangGraph and Langflow to track all AI agent operations, decisions, and state changes in BuiltEnvironment.ai.

---

## LangGraph Audit Integration

### LangGraph Built-in Audit Capabilities

LangGraph provides several built-in features for audit trails:

1. **State Persistence**: Complete state history at each node
2. **Checkpointing**: Automatic state snapshots for recovery and replay
3. **Time-Travel Debugging**: Ability to inspect historical states
4. **Execution Trace**: Complete path through the graph with timestamps

### Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                  LangGraph Agent                           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │  Node 1  │───▶│  Node 2  │───▶│  Node 3  │           │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘           │
│       │               │               │                   │
│       ▼               ▼               ▼                   │
│  ┌────────────────────────────────────────────┐          │
│  │       Checkpoint Manager (Built-in)        │          │
│  └─────────────────┬──────────────────────────┘          │
└────────────────────┼─────────────────────────────────────┘
                     │
                     ▼
       ┌─────────────────────────────┐
       │  Audit Event Collector       │
       │  (Custom Integration)        │
       └─────────────┬────────────────┘
                     │
                     ▼
       ┌─────────────────────────────┐
       │  Audit Database              │
       │  (TimescaleDB)               │
       └──────────────────────────────┘
```

---

## LangGraph Checkpointing Integration

### Setup with Audit Logging

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.base import CheckpointMetadata
import asyncio
from datetime import datetime
from typing import Dict, Any
import uuid

# Custom checkpoint saver with audit integration
class AuditCheckpointSaver(PostgresSaver):
    """PostgreSQL checkpoint saver with audit logging"""

    def __init__(self, connection_string: str, audit_logger):
        super().__init__(connection_string)
        self.audit_logger = audit_logger

    async def aput(
        self,
        config: Dict,
        checkpoint: Dict[str, Any],
        metadata: CheckpointMetadata
    ) -> None:
        """Save checkpoint and create audit event"""

        # Save checkpoint using parent class
        await super().aput(config, checkpoint, metadata)

        # Create audit event
        await self.audit_logger.log_event({
            "audit_id": str(uuid.uuid4()),
            "event_type": "agent.checkpoint.created",
            "timestamp": datetime.utcnow().isoformat(),

            "actor": {
                "type": "agent",
                "id": config.get("agent_id"),
                "name": config.get("agent_name", "Unknown Agent")
            },

            "target": {
                "type": "workflow",
                "id": config.get("thread_id"),
                "name": config.get("workflow_name")
            },

            "action": {
                "verb": "execute",
                "description": f"Checkpoint created at node: {metadata.get('node')}",
                "status": "success"
            },

            "context": {
                "tenant_id": config.get("tenant_id"),
                "project_id": config.get("project_id"),
                "request_id": config.get("request_id")
            },

            "ai_specific": {
                "agent_type": config.get("agent_type"),
                "checkpoint_id": metadata.get("checkpoint_id"),
                "parent_checkpoint_id": metadata.get("parent_checkpoint_id"),
                "node": metadata.get("node"),
                "step": metadata.get("step"),
                "state_keys": list(checkpoint.keys()),
                "state_size_bytes": len(str(checkpoint))
            },

            "data": {
                "after": {
                    "checkpoint_id": metadata.get("checkpoint_id"),
                    "step": metadata.get("step"),
                    "status": "saved"
                },
                "metadata": metadata
            }
        })

    async def aget(self, config: Dict) -> Optional[Dict]:
        """Retrieve checkpoint and log access"""

        checkpoint = await super().aget(config)

        if checkpoint:
            await self.audit_logger.log_event({
                "event_type": "agent.checkpoint.retrieved",
                "actor": {"type": "system"},
                "action": {"verb": "read", "status": "success"},
                "ai_specific": {
                    "checkpoint_id": checkpoint.get("id"),
                    "retrieved_for": config.get("agent_id")
                }
            })

        return checkpoint


# Usage in LangGraph workflow
from audit_logger import AuditLogger

async def create_audited_workflow():
    """Create LangGraph workflow with audit logging"""

    # Initialize audit logger
    audit_logger = AuditLogger(
        timescale_connection="postgresql://...",
        elasticsearch_connection="http://..."
    )

    # Initialize checkpoint saver with audit integration
    checkpointer = AuditCheckpointSaver(
        connection_string="postgresql://...",
        audit_logger=audit_logger
    )

    # Define the workflow
    workflow = StateGraph(...)

    # Compile with checkpointing
    app = workflow.compile(checkpointer=checkpointer)

    return app, audit_logger
```

---

## Node-Level Audit Logging

### Audit Every Node Execution

```python
from functools import wraps
from time import time

def audit_node(node_name: str, agent_type: str):
    """Decorator to audit node execution"""

    def decorator(func):
        @wraps(func)
        async def wrapper(state: Dict, config: Dict, audit_logger: AuditLogger):
            start_time = time()
            audit_id = str(uuid.uuid4())

            # Log node start
            await audit_logger.log_event({
                "audit_id": audit_id,
                "event_type": "agent.node.started",
                "timestamp": datetime.utcnow().isoformat(),

                "actor": {
                    "type": "agent",
                    "id": config.get("agent_id"),
                    "name": config.get("agent_name")
                },

                "action": {
                    "verb": "execute",
                    "description": f"Node '{node_name}' started",
                    "status": "in_progress"
                },

                "ai_specific": {
                    "agent_type": agent_type,
                    "node": node_name,
                    "state_keys": list(state.keys())
                }
            })

            try:
                # Execute node logic
                result = await func(state)

                execution_time = (time() - start_time) * 1000

                # Log node completion
                await audit_logger.log_event({
                    "audit_id": str(uuid.uuid4()),
                    "event_type": "agent.node.completed",
                    "timestamp": datetime.utcnow().isoformat(),

                    "actor": {
                        "type": "agent",
                        "id": config.get("agent_id"),
                        "name": config.get("agent_name")
                    },

                    "action": {
                        "verb": "execute",
                        "description": f"Node '{node_name}' completed successfully",
                        "status": "success"
                    },

                    "context": {
                        "parent_audit_id": audit_id
                    },

                    "ai_specific": {
                        "agent_type": agent_type,
                        "node": node_name,
                        "execution_time_ms": execution_time,
                        "state_changes": get_state_changes(state, result)
                    },

                    "data": {
                        "before": state,
                        "after": result,
                        "changes": list(set(result.keys()) - set(state.keys()))
                    },

                    "performance": {
                        "response_time_ms": execution_time
                    }
                })

                return result

            except Exception as e:
                execution_time = (time() - start_time) * 1000

                # Log node failure
                await audit_logger.log_event({
                    "audit_id": str(uuid.uuid4()),
                    "event_type": "agent.node.failed",
                    "timestamp": datetime.utcnow().isoformat(),

                    "actor": {
                        "type": "agent",
                        "id": config.get("agent_id"),
                        "name": config.get("agent_name")
                    },

                    "action": {
                        "verb": "execute",
                        "description": f"Node '{node_name}' failed",
                        "status": "failure",
                        "error": str(e)
                    },

                    "context": {
                        "parent_audit_id": audit_id
                    },

                    "ai_specific": {
                        "agent_type": agent_type,
                        "node": node_name,
                        "execution_time_ms": execution_time,
                        "error_type": type(e).__name__,
                        "error_trace": traceback.format_exc()
                    },

                    "performance": {
                        "response_time_ms": execution_time
                    }
                })

                raise

        return wrapper
    return decorator


# Usage in workflow definition
@audit_node("analyze_structure", "structural_engineering")
async def analyze_structure_node(state: Dict) -> Dict:
    """Structural analysis node with audit logging"""
    # Node logic here
    return updated_state
```

---

## Tool Call Auditing

### Track All Tool Invocations

```python
from langchain.tools import BaseTool

class AuditedTool(BaseTool):
    """Base tool with audit logging"""

    def __init__(self, *args, audit_logger: AuditLogger, **kwargs):
        super().__init__(*args, **kwargs)
        self.audit_logger = audit_logger

    async def _arun(self, *args, **kwargs) -> Any:
        """Run tool with audit logging"""

        audit_id = str(uuid.uuid4())
        start_time = time()

        # Log tool call start
        await self.audit_logger.log_event({
            "audit_id": audit_id,
            "event_type": "agent.tool.called",
            "timestamp": datetime.utcnow().isoformat(),

            "actor": {
                "type": "agent",
                "id": kwargs.get("agent_id", "unknown")
            },

            "action": {
                "verb": "execute",
                "description": f"Tool '{self.name}' invoked",
                "status": "in_progress"
            },

            "ai_specific": {
                "tool_name": self.name,
                "tool_description": self.description,
                "input_args": str(args)[:500],  # Truncate long inputs
                "input_kwargs": {k: str(v)[:100] for k, v in kwargs.items()}
            }
        })

        try:
            # Execute tool
            result = await super()._arun(*args, **kwargs)

            execution_time = (time() - start_time) * 1000

            # Log tool success
            await self.audit_logger.log_event({
                "audit_id": str(uuid.uuid4()),
                "event_type": "agent.tool.completed",
                "timestamp": datetime.utcnow().isoformat(),

                "action": {
                    "verb": "execute",
                    "description": f"Tool '{self.name}' completed",
                    "status": "success"
                },

                "context": {
                    "parent_audit_id": audit_id
                },

                "ai_specific": {
                    "tool_name": self.name,
                    "execution_time_ms": execution_time,
                    "result_type": type(result).__name__,
                    "result_size": len(str(result))
                },

                "performance": {
                    "response_time_ms": execution_time
                }
            })

            return result

        except Exception as e:
            execution_time = (time() - start_time) * 1000

            # Log tool failure
            await self.audit_logger.log_event({
                "audit_id": str(uuid.uuid4()),
                "event_type": "agent.tool.failed",
                "timestamp": datetime.utcnow().isoformat(),

                "action": {
                    "verb": "execute",
                    "description": f"Tool '{self.name}' failed",
                    "status": "failure",
                    "error": str(e)
                },

                "context": {
                    "parent_audit_id": audit_id
                },

                "ai_specific": {
                    "tool_name": self.name,
                    "execution_time_ms": execution_time,
                    "error_type": type(e).__name__
                },

                "performance": {
                    "response_time_ms": execution_time
                }
            })

            raise
```

---

## Langflow Audit Integration

### Langflow Webhook Configuration

Langflow can send events to external systems via webhooks for every workflow execution.

**Langflow Configuration** (`langflow_config.yaml`):

```yaml
# Langflow Audit Configuration
observability:
  enabled: true

  # Webhook for audit events
  webhooks:
    - name: "audit_system"
      url: "https://api.builtenvironment.ai/audit/webhook/langflow"
      headers:
        Authorization: "Bearer ${AUDIT_WEBHOOK_TOKEN}"
        Content-Type: "application/json"

      events:
        - "flow.started"
        - "flow.completed"
        - "flow.failed"
        - "flow.timeout"
        - "component.executed"
        - "component.failed"

  # LangWatch integration for observability
  langwatch:
    enabled: true
    api_key: "${LANGWATCH_API_KEY}"
    project_id: "builtenvironment-ai"

  # Langfuse integration for trace management
  langfuse:
    enabled: true
    public_key: "${LANGFUSE_PUBLIC_KEY}"
    secret_key: "${LANGFUSE_SECRET_KEY}"
    host: "https://cloud.langfuse.com"

# Workflow-level audit settings
workflows:
  audit_all_executions: true
  log_input_output: true
  log_intermediate_steps: true
  retention_days: 90
```

### Webhook Handler Implementation

```python
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import hmac
import hashlib

router = APIRouter()

class LangflowWebhookEvent(BaseModel):
    """Langflow webhook event schema"""
    event_type: str
    flow_id: str
    flow_name: str
    execution_id: str
    timestamp: str
    user_id: Optional[str]
    tenant_id: Optional[str]
    status: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]


def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify webhook signature for security"""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)


@router.post("/audit/webhook/langflow")
async def langflow_webhook_handler(
    event: LangflowWebhookEvent,
    authorization: str = Header(...),
    x_signature: Optional[str] = Header(None)
):
    """Handle Langflow webhook events and create audit entries"""

    # Verify authorization
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization")

    token = authorization.replace("Bearer ", "")
    if token != os.getenv("AUDIT_WEBHOOK_TOKEN"):
        raise HTTPException(status_code=403, detail="Invalid token")

    # Verify signature if provided
    if x_signature:
        payload = event.json()
        if not verify_webhook_signature(payload, x_signature, os.getenv("WEBHOOK_SECRET")):
            raise HTTPException(status_code=403, detail="Invalid signature")

    # Transform Langflow event to audit event format
    audit_event = transform_langflow_event(event)

    # Store in audit database
    await audit_logger.log_event(audit_event)

    return {"status": "success", "audit_id": audit_event["audit_id"]}


def transform_langflow_event(event: LangflowWebhookEvent) -> Dict:
    """Transform Langflow webhook to audit event format"""

    event_type_mapping = {
        "flow.started": "workflow.started",
        "flow.completed": "workflow.completed",
        "flow.failed": "workflow.failed",
        "flow.timeout": "workflow.timeout",
        "component.executed": "workflow.node.executed",
        "component.failed": "workflow.node.failed"
    }

    return {
        "audit_id": str(uuid.uuid4()),
        "event_type": event_type_mapping.get(event.event_type, event.event_type),
        "timestamp": event.timestamp,

        "actor": {
            "type": "agent",
            "id": event.flow_id,
            "name": event.flow_name
        },

        "target": {
            "type": "workflow",
            "id": event.execution_id,
            "name": event.flow_name
        },

        "action": {
            "verb": "execute",
            "description": f"Langflow workflow '{event.flow_name}' {event.status}",
            "status": map_status(event.status)
        },

        "context": {
            "tenant_id": event.tenant_id,
            "user_id": event.user_id,
            "request_id": event.execution_id
        },

        "ai_specific": {
            "workflow_id": event.flow_id,
            "execution_id": event.execution_id,
            "langflow_data": event.data,
            "metadata": event.metadata
        },

        "data": {
            "after": {
                "status": event.status,
                "flow_name": event.flow_name
            },
            "metadata": event.metadata
        }
    }


def map_status(langflow_status: str) -> str:
    """Map Langflow status to audit status"""
    mapping = {
        "running": "in_progress",
        "completed": "success",
        "failed": "failure",
        "timeout": "failure"
    }
    return mapping.get(langflow_status, "unknown")
```

---

## LangSmith Integration

### LangSmith for Enhanced Observability

LangSmith provides comprehensive observability for LangChain/LangGraph applications.

```python
import os
from langsmith import Client

# Initialize LangSmith client
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "builtenvironment-ai"

langsmith_client = Client()


async def sync_langsmith_to_audit():
    """Periodically sync LangSmith traces to audit system"""

    # Query recent runs from LangSmith
    runs = langsmith_client.list_runs(
        project_name="builtenvironment-ai",
        start_time=datetime.now() - timedelta(hours=1)
    )

    for run in runs:
        # Transform LangSmith run to audit event
        audit_event = {
            "audit_id": str(uuid.uuid4()),
            "event_type": "agent.execution.traced",
            "timestamp": run.start_time.isoformat(),

            "actor": {
                "type": "agent",
                "id": run.id,
                "name": run.name
            },

            "ai_specific": {
                "langsmith_run_id": str(run.id),
                "run_type": run.run_type,
                "inputs": run.inputs,
                "outputs": run.outputs,
                "error": run.error,
                "prompt_tokens": run.prompt_tokens,
                "completion_tokens": run.completion_tokens,
                "total_tokens": run.total_tokens,
                "execution_time_ms": (run.end_time - run.start_time).total_seconds() * 1000
            },

            "performance": {
                "response_time_ms": (run.end_time - run.start_time).total_seconds() * 1000
            }
        }

        await audit_logger.log_event(audit_event)
```

---

## Complete Example: Audited Structural Analysis Agent

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

# State definition
class StructuralAnalysisState(TypedDict):
    document_id: str
    document_content: str
    load_calculations: Annotated[list, operator.add]
    compliance_issues: Annotated[list, operator.add]
    recommendations: Annotated[list, operator.add]
    status: str


# Define nodes with audit logging
@audit_node("extract_specifications", "structural_engineering")
async def extract_specifications(state: StructuralAnalysisState) -> Dict:
    """Extract structural specifications from document"""
    # Implementation here
    return {"specifications": [...]}


@audit_node("validate_loads", "structural_engineering")
async def validate_loads(state: StructuralAnalysisState) -> Dict:
    """Validate load calculations"""
    # Implementation here
    return {"load_calculations": [...]}


@audit_node("check_eurocode", "structural_engineering")
async def check_eurocode(state: StructuralAnalysisState) -> Dict:
    """Check Eurocode compliance"""
    # Implementation here
    return {"compliance_issues": [...]}


@audit_node("generate_recommendations", "structural_engineering")
async def generate_recommendations(state: StructuralAnalysisState) -> Dict:
    """Generate recommendations"""
    # Implementation here
    return {"recommendations": [...], "status": "completed"}


# Build workflow with audit integration
async def create_structural_analysis_workflow():
    """Create fully audited structural analysis workflow"""

    # Initialize audit logger
    audit_logger = AuditLogger(...)

    # Initialize checkpoint saver with audit
    checkpointer = AuditCheckpointSaver(
        connection_string="postgresql://...",
        audit_logger=audit_logger
    )

    # Build graph
    workflow = StateGraph(StructuralAnalysisState)

    # Add nodes
    workflow.add_node("extract_specs", extract_specifications)
    workflow.add_node("validate_loads", validate_loads)
    workflow.add_node("check_eurocode", check_eurocode)
    workflow.add_node("generate_recs", generate_recommendations)

    # Add edges
    workflow.set_entry_point("extract_specs")
    workflow.add_edge("extract_specs", "validate_loads")
    workflow.add_edge("validate_loads", "check_eurocode")
    workflow.add_edge("check_eurocode", "generate_recs")
    workflow.add_edge("generate_recs", END)

    # Compile with checkpointing
    app = workflow.compile(checkpointer=checkpointer)

    return app, audit_logger


# Execute workflow
async def run_structural_analysis(document_id: str, user_id: str, project_id: str):
    """Run structural analysis with complete audit trail"""

    app, audit_logger = await create_structural_analysis_workflow()

    # Configuration with audit context
    config = {
        "configurable": {
            "thread_id": f"structural-{document_id}",
            "agent_id": "structural-agent-01",
            "agent_name": "Structural Engineering Agent",
            "agent_type": "structural_engineering",
            "user_id": user_id,
            "project_id": project_id,
            "tenant_id": get_tenant_id(user_id)
        }
    }

    # Initial state
    initial_state = {
        "document_id": document_id,
        "document_content": await load_document(document_id),
        "load_calculations": [],
        "compliance_issues": [],
        "recommendations": [],
        "status": "started"
    }

    # Log workflow start
    await audit_logger.log_event({
        "event_type": "workflow.started",
        "actor": {"type": "agent", "id": "structural-agent-01"},
        "context": {"project_id": project_id, "user_id": user_id},
        "ai_specific": {"workflow_name": "structural_analysis"}
    })

    try:
        # Execute workflow (fully audited via checkpoints and node decorators)
        result = await app.ainvoke(initial_state, config=config)

        # Log workflow completion
        await audit_logger.log_event({
            "event_type": "workflow.completed",
            "action": {"status": "success"},
            "ai_specific": {
                "workflow_name": "structural_analysis",
                "results_count": len(result.get("recommendations", []))
            }
        })

        return result

    except Exception as e:
        # Log workflow failure
        await audit_logger.log_event({
            "event_type": "workflow.failed",
            "action": {"status": "failure", "error": str(e)},
            "ai_specific": {"workflow_name": "structural_analysis"}
        })
        raise
```

---

## Query Audit Trails

### Retrieve Complete Agent Execution History

```python
async def get_agent_execution_history(
    agent_id: str,
    start_time: datetime,
    end_time: datetime
) -> List[Dict]:
    """Get complete execution history for an agent"""

    query = """
    SELECT *
    FROM audit_events
    WHERE actor.id = $1
      AND event_type LIKE 'agent.%'
      AND timestamp BETWEEN $2 AND $3
    ORDER BY timestamp ASC
    """

    return await db.fetch_all(query, agent_id, start_time, end_time)


async def get_workflow_trace(execution_id: str) -> Dict:
    """Get complete trace of a workflow execution"""

    query = """
    SELECT *
    FROM audit_events
    WHERE context.request_id = $1
       OR target.id = $1
    ORDER BY timestamp ASC
    """

    events = await db.fetch_all(query, execution_id)

    # Build execution tree
    return build_execution_tree(events)


def build_execution_tree(events: List[Dict]) -> Dict:
    """Build hierarchical execution tree from flat event list"""

    root = {"events": []}
    event_map = {}

    for event in events:
        event_id = event["audit_id"]
        parent_id = event.get("context", {}).get("parent_audit_id")

        event_map[event_id] = event
        event["children"] = []

        if parent_id and parent_id in event_map:
            event_map[parent_id]["children"].append(event)
        else:
            root["events"].append(event)

    return root
```

---

## Best Practices

### 1. Performance Optimization

- **Batch audit writes**: Buffer events and write in batches (every 5 seconds or 100 events)
- **Async logging**: Never block application flow for audit logging
- **Sampling**: For high-frequency events, consider sampling (log 1% of reads, 100% of writes)

### 2. Privacy Considerations

- **Never log PII in plain text**: Hash or tokenize sensitive data
- **Never log document content**: Only log metadata and references
- **Respect GDPR**: Provide mechanisms for data export and deletion

### 3. Security

- **Sign audit events**: Use HMAC or digital signatures to prevent tampering
- **Encrypt sensitive fields**: Encrypt IP addresses, user agents, etc.
- **Restrict access**: Only authorized personnel can access audit logs

### 4. Reliability

- **Audit the audit system**: Monitor audit pipeline health
- **Failover**: If audit system fails, queue events for later processing
- **Validate completeness**: Periodic checks for missing audit events

---

## Summary

This integration provides:

✅ **Complete AI agent traceability** with LangGraph checkpoints and node execution logs
✅ **Langflow workflow monitoring** via webhooks and observability integrations
✅ **Tool call tracking** for all external tool invocations
✅ **Time-travel debugging** with full state history
✅ **Compliance-ready audit trails** meeting GDPR and ISO requirements
✅ **Performance insights** with execution time tracking
✅ **Security monitoring** for anomaly detection

All AI agent operations are fully auditable with "who did what, when, where, and why."

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-27

# Agent Architecture - BuiltEnvironment.ai

## TWO TYPES OF AGENTS

This platform has **TWO COMPLETELY DIFFERENT** types of agents that serve different purposes:

### 1. Claude Code Development Agents (.claude/agents/)
**Purpose**: Help BUILD the application
**Location**: `.claude/agents/`
**Technology**: Claude Code IDE agents
**Users**: Developers building the platform

These are development assistants that help developers write code, debug, test, and deploy the application itself.

### 2. Langflow Specialist Agents (Product Agents)
**Purpose**: RUN WITHIN the application to check compliance
**Location**: Langflow workflows + backend integration
**Technology**: Langflow + Claude API
**Users**: End users (consultants, developers, building professionals)

These are the 13 specialized compliance checking agents that analyze building documents.

---

## 1. CLAUDE CODE DEVELOPMENT AGENTS

These agents help developers BUILD the platform.

### Agent List:

1. **backend-developer** - FastAPI, database, API development
2. **frontend-developer** - React, TypeScript, UI components
3. **langflow-integrator** - Langflow workflow creation and integration
4. **database-architect** - PostgreSQL schema, migrations, optimization
5. **ai-engineer** - Claude API, RAG system, embeddings
6. **devops-engineer** - Docker, deployment, CI/CD
7. **test-engineer** - Testing, quality assurance
8. **documentation-writer** - Technical documentation

### Usage Example:
```bash
# In Claude Code IDE
/agent backend-developer "Create a new API endpoint for project validation"
/agent langflow-integrator "Set up fire safety agent workflow"
```

---

## 2. LANGFLOW SPECIALIST AGENTS (Product Agents)

These agents RUN IN THE PRODUCT to analyze building documents.

### The 13 Specialist Compliance Agents:

1. **Structural Engineering Agent** - Part A compliance, Eurocodes
2. **Building Envelope Agent** - Parts C & L, thermal performance
3. **Mechanical Services Agent** - Parts F, G, H, J (HVAC, plumbing, drainage)
4. **Electrical Services Agent** - Part P, BS 7671, low voltage systems
5. **Fire Safety Agent** - Part B (B1-B5), fire safety strategy
6. **Accessibility Agent** - Part M, BS 8300, inclusive design
7. **Environmental & Sustainability Agent** - Part L, BREEAM, LEED
8. **Health & Safety Agent** - CDM 2015, H&S compliance
9. **Quality Assurance Agent** - Testing, commissioning, certifications
10. **Legal & Contracts Agent** - Contracts, warranties, statutory compliance
11. **Specialist Systems Agent** - Lifts, BMS, specialist equipment
12. **External Works Agent** - Drainage, landscaping, highways
13. **Finishes & Interiors Agent** - Part E (acoustics), internal finishes

### Architecture Flow:

```
User uploads document
    ↓
FastAPI Backend receives file
    ↓
Document processed (text extraction, chunking)
    ↓
Document sent to Langflow
    ↓
Langflow Master Orchestration Workflow
    ├→ Document Classification
    ├→ Routing to relevant specialist agents
    ├→ Parallel processing by multiple agents
    ├→ Cross-discipline conflict detection
    └→ Report aggregation
    ↓
Results returned to FastAPI
    ↓
Stored in PostgreSQL (compliance_findings)
    ↓
User sees traffic light results 🟢🟡🔴
```

### Langflow Integration Points:

1. **Webhook Endpoint**: FastAPI → Langflow
   ```python
   POST /api/v1/langflow/analyze
   {
     "document_id": "uuid",
     "document_text": "extracted text",
     "agents_to_run": ["fire_safety", "structural"]
   }
   ```

2. **Langflow Workflows**: Each agent is a Langflow flow
   - `fire-safety-agent.json` - Part B compliance workflow
   - `structural-agent.json` - Part A compliance workflow
   - `electrical-agent.json` - Part P compliance workflow
   - ... (11 more)

3. **Result Webhook**: Langflow → FastAPI
   ```python
   POST /api/v1/langflow/webhook/results
   {
     "document_id": "uuid",
     "agent_id": "fire_safety",
     "findings": [...],
     "overall_status": "amber",
     "confidence": 0.85
   }
   ```

---

## CURRENT IMPLEMENTATION STATUS

### ✅ What's Built:

**Backend (FastAPI)**:
- Authentication ✅
- Multi-tenancy ✅
- Document upload ✅
- Text extraction ✅
- ChromaDB RAG ✅
- PostgreSQL models ✅
- Audit logging ✅

**Fire Safety Agent**:
- LangGraph implementation (Python) ✅
- Part B compliance checking ✅
- Traffic light system ✅
- BUT: This is in Python, NOT in Langflow!

### ❌ What's Missing:

**Langflow Integration**:
- Langflow installation/deployment ❌
- Langflow workflow definitions (JSON) ❌
- FastAPI → Langflow communication ❌
- Webhook handlers for Langflow results ❌

**Remaining 12 Agents**:
- All need to be created in Langflow ❌

**Claude Code Dev Agents**:
- Development helper agents in .claude/agents/ ❌

---

## WHAT NEEDS TO BE DONE

### Priority 1: Understand the Architecture

**Read these docs**:
- `/docs/architecture/claude-langflow-architecture.md` ✅
- `/docs/implementation/langflow-workflows-specification.md` ✅
- `/docs/compliance/ai-agent-discipline-mapping.md` ✅
- All other `/docs/` files

### Priority 2: Create Claude Code Development Agents

Create 8 agents in `.claude/agents/`:
1. `backend-developer.md`
2. `frontend-developer.md`
3. `langflow-integrator.md`
4. `database-architect.md`
5. `ai-engineer.md`
6. `devops-engineer.md`
7. `test-engineer.md`
8. `documentation-writer.md`

### Priority 3: Set Up Langflow

1. Add Langflow to docker-compose.yml
2. Install Langflow service
3. Configure Langflow API connection
4. Create webhook endpoints in FastAPI

### Priority 4: Create Langflow Workflows

For each of the 13 specialist agents, create:
1. Langflow workflow JSON definition
2. Agent-specific nodes and logic
3. Integration with Claude API
4. Output formatting (traffic light system)

### Priority 5: Backend Integration

Update FastAPI backend:
1. Add Langflow client
2. Create document → Langflow routing
3. Add webhook handlers for results
4. Update document processing pipeline
5. Replace Python LangGraph with Langflow calls

---

## FILE STRUCTURE

```
BuiltEnvironment.ai/
├── .claude/
│   ├── agents/                    # Claude Code dev agents
│   │   ├── backend-developer.md
│   │   ├── frontend-developer.md
│   │   ├── langflow-integrator.md
│   │   └── ... (8 total)
│   ├── commands/                  # Slash commands (already exist)
│   └── skills/                    # Claude skills (already exist)
│
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── langflow_client.py      # NEW: Langflow API client
│   │   │   ├── agent_router.py         # NEW: Route docs to agents
│   │   │   └── ai_agents/
│   │   │       └── fire_safety_agent.py # REMOVE: Move to Langflow
│   │   ├── api/v1/endpoints/
│   │   │   └── langflow.py             # NEW: Langflow webhooks
│   │   └── ...
│   └── ...
│
├── langflow/                       # NEW: Langflow workflows
│   ├── flows/
│   │   ├── master-orchestration.json
│   │   ├── structural-agent.json
│   │   ├── fire-safety-agent.json
│   │   ├── electrical-agent.json
│   │   └── ... (13 specialist agents)
│   └── README.md
│
├── docs/
│   ├── architecture/
│   ├── compliance/
│   └── implementation/
│
└── docker-compose.yml             # ADD: Langflow service
```

---

## IMPLEMENTATION PLAN

### Step 1: Create Claude Code Development Agents (1 hour)
Create 8 markdown files in `.claude/agents/` to help developers build the platform.

### Step 2: Set Up Langflow Infrastructure (2 hours)
- Add Langflow to docker-compose
- Configure Langflow service
- Test Langflow API access

### Step 3: Create Master Orchestration Workflow (3 hours)
- Document classification
- Agent routing logic
- Parallel processing coordination
- Result aggregation

### Step 4: Create First Langflow Agent - Fire Safety (4 hours)
- Migrate existing Python logic to Langflow
- Create workflow JSON
- Test with sample documents
- Validate traffic light output

### Step 5: Create Remaining 12 Agents (2 days)
- One agent per hour
- Follow fire safety pattern
- Test each individually

### Step 6: Backend Integration (1 day)
- Langflow client
- Webhook handlers
- Document routing
- Result storage

### Step 7: Testing & Validation (1 day)
- End-to-end testing
- Multi-agent coordination
- Performance optimization

**Total Time: ~5 days**

---

## KEY INSIGHTS

1. **The Fire Safety Agent I built in Python needs to be recreated in Langflow**
   - Current: Python file with LangGraph
   - Needed: Langflow workflow JSON

2. **Langflow is the "AI Brain"**
   - All 13 agents run IN Langflow
   - FastAPI is the "data layer" and API
   - Langflow handles orchestration and AI processing

3. **Development Agents vs Product Agents**
   - Dev agents: Help build the app
   - Product agents: Run IN the app

4. **Current Python fire_safety_agent.py is a prototype**
   - Good for understanding the logic
   - Needs to be converted to Langflow format
   - Can be used as reference for Langflow implementation

---

## NEXT IMMEDIATE ACTIONS

1. ✅ **Understand the architecture** (DONE - this document!)
2. **Create Claude Code dev agents** (.claude/agents/)
3. **Set up Langflow in docker-compose**
4. **Create Langflow client in backend**
5. **Convert fire safety agent to Langflow**
6. **Create remaining 12 agents in Langflow**

This document serves as the master reference for the agent architecture!

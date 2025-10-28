# Master Orchestration Workflow - Langflow

## Overview

The Master Orchestration Workflow is the central coordinator that manages document processing, routes documents to appropriate specialist agents, aggregates findings, and generates comprehensive compliance reports for the BuiltEnvironment.ai platform.

## Workflow Architecture

```
User uploads document
    ↓
FastAPI Backend (document upload endpoint)
    ↓
Master Orchestration Workflow (Langflow)
    ├→ Document Upload Handler (authenticate, validate)
    ├→ Document Classifier (identify type and disciplines)
    ├→ Routing Engine (determine which specialist agents to invoke)
    ├→ Parallel Agent Execution
    │   ├→ Structural Agent (if structural content detected)
    │   ├→ Fire Safety Agent (if fire safety content detected)
    │   ├→ Building Envelope Agent (if envelope content detected)
    │   ├→ Mechanical Services Agent (if M&E content detected)
    │   ├→ Electrical Services Agent (if electrical content detected)
    │   ├→ Accessibility Agent (if access requirements detected)
    │   ├→ Environmental & Sustainability Agent (if sustainability content detected)
    │   ├→ Health & Safety Agent (if H&S content detected)
    │   ├→ Quality Assurance Agent (if testing/commissioning content detected)
    │   ├→ Legal & Contracts Agent (if contractual content detected)
    │   ├→ Specialist Systems Agent (if lifts/BMS/security detected)
    │   ├→ External Works Agent (if drainage/landscaping detected)
    │   └→ Finishes & Interiors Agent (if finishes/acoustics detected)
    ├→ Cross-Discipline Conflict Detection
    ├→ Report Aggregation
    ├→ Traffic Light Scoring (Overall status)
    └→ Results returned to FastAPI Backend
    ↓
Stored in PostgreSQL (compliance_findings JSONB)
    ↓
Displayed to User in WYSIWYG editor
```

## Master Orchestration Nodes

### 1. Document Upload Handler Node
**Purpose**: Receives and validates uploaded documents

**Inputs:**
- Document file (PDF, DWG, DOCX)
- User authentication token (tenant_id, user_id)
- Project metadata (project_id, building type, location)

**Processing:**
- User authentication and authorization
- Virus scanning
- File format validation
- Text extraction (Tesseract OCR for images, PyPDF2/pdfplumber for PDFs)
- Document metadata extraction (filename, pages, file size)

**Outputs:**
- Validated document object
- Extracted text
- User context (tenant_id, user_id, project_id)

---

### 2. Document Classifier Node
**Purpose**: Classifies document type and identifies relevant building disciplines

**Component**: `DocumentClassifier` (custom component in `langflow/components/document_classifier.py`)

**Inputs:**
- Extracted document text
- Document filename and metadata
- Project building type

**Processing:**
- Document type classification:
  - Drawing (architectural, structural, M&E)
  - Specification
  - Calculation sheet
  - Fire strategy
  - Schedule (door, window, finishes)
  - Certificate (test, commissioning)
  - Report (inspection, survey)
- Discipline detection using keyword analysis:
  - Structural keywords → Structural Agent
  - Fire keywords → Fire Safety Agent
  - Thermal/insulation keywords → Building Envelope Agent
  - HVAC/plumbing keywords → Mechanical Services Agent
  - Electrical keywords → Electrical Services Agent
  - Accessibility keywords → Accessibility Agent
  - Sustainability keywords → Environmental Agent
  - etc.
- Regulation mapping (Parts A-P, Eurocodes, British Standards)

**Outputs:**
- Document classification
- List of disciplines detected
- List of regulations applicable
- Agents to invoke

---

### 3. Routing Engine Node
**Purpose**: Determines which specialist agents to invoke and orchestrates parallel execution

**Inputs:**
- Document classification results
- Disciplines detected
- User preferences (which agents to enable)
- Project requirements

**Processing:**
- Priority assignment:
  - Critical agents (e.g., Fire Safety for fire strategy documents)
  - Standard agents (e.g., Structural for most building documents)
  - Optional agents (e.g., Environmental for non-BREEAM projects)
- Resource allocation (limit concurrent agents to avoid overload)
- Parallel vs. sequential execution planning

**Outputs:**
- Routing instructions for each agent
- Execution plan (parallel batches)
- Priority levels

---

### 4. Specialist Agent Orchestration Node
**Purpose**: Manages parallel execution of specialist compliance agents

**Processing:**
Each specialist agent receives:
- Document text
- Relevant sections/chapters (pre-filtered)
- Building metadata (height, occupancy, construction type)
- Tenant_id for multi-tenant isolation

**Specialist Agents Executed:**
1. **Structural Agent** → Part A, Eurocodes (structural drawings, calculations)
2. **Fire Safety Agent** → Part B (fire strategies, protection systems)
3. **Building Envelope Agent** → Parts C & L (thermal performance, U-values)
4. **Mechanical Services Agent** → Parts F, G, H, J (HVAC, plumbing, drainage)
5. **Electrical Services Agent** → Part P, BS 7671 (electrical installations)
6. **Accessibility Agent** → Part M, BS 8300 (accessible design)
7. **Environmental & Sustainability Agent** → Part L, BREEAM (energy, carbon)
8. **Health & Safety Agent** → CDM 2015 (construction health & safety)
9. **Quality Assurance Agent** → Testing, commissioning, certification
10. **Legal & Contracts Agent** → JCT/NEC contracts, warranties
11. **Specialist Systems Agent** → Lifts (LOLER), BMS, security systems
12. **External Works Agent** → Drainage, SuDS, landscaping
13. **Finishes & Interiors Agent** → Part E (acoustics), finishes

**Each Agent Returns:**
- List of compliance findings (regulation, requirement, is_compliant, confidence, evidence)
- Agent-specific metrics
- Processing time and status

---

### 5. Cross-Discipline Conflict Detection Node
**Purpose**: Identifies conflicts between different discipline requirements

**Inputs:**
- All specialist agent findings
- Building design constraints

**Processing:**
- **Structural vs. Architectural**: Beam depths conflicting with ceiling heights
- **Fire Safety vs. Accessibility**: Fire door closing force vs. accessible opening force
- **M&E vs. Structural**: Service penetrations through fire-rated floors
- **Building Envelope vs. Fire Safety**: External wall insulation combustibility
- **Electrical vs. Plumbing**: Services clash detection

**Conflict Detection Logic:**
```python
if structural_agent.beam_depth > architectural_agent.ceiling_height:
    conflict = {
        "type": "structural_architectural_clash",
        "severity": "high",
        "description": "Beam depth exceeds available ceiling height",
        "agents_involved": ["structural", "architectural"],
        "recommendation": "Reduce beam depth or increase floor-to-floor height"
    }
```

**Outputs:**
- List of cross-discipline conflicts
- Severity ratings (low, medium, high, critical)
- Resolution recommendations

---

### 6. Report Aggregation Node
**Purpose**: Combines all agent findings into structured compliance report

**Inputs:**
- All specialist agent findings
- Cross-discipline conflicts
- Document classification
- User project details

**Processing:**
- **Overall Compliance Status Calculation**:
  - If ANY finding is RED → Overall RED
  - If no RED but ANY AMBER → Overall AMBER
  - If all GREEN → Overall GREEN
- **Findings Organization by Regulation**:
  - Part A (Structural)
  - Part B (Fire Safety)
  - Part C (Moisture Protection)
  - Part E (Acoustics)
  - Part F-J (Building Services)
  - Part L (Energy)
  - Part M (Accessibility)
  - Part P (Electrical)
- **Summary Statistics**:
  - Total findings: 47
  - Green: 38 (81%)
  - Amber: 6 (13%)
  - Red: 3 (6%)
  - Average confidence: 0.87
- **Priority Action List**:
  - Critical (RED findings requiring immediate action)
  - High (AMBER findings needing professional review)
  - Medium (Low-confidence GREEN findings)
  - Low (High-confidence GREEN findings)

**Output Format** (JSON):
```json
{
  "document_id": "uuid",
  "overall_status": "amber",
  "overall_confidence": 0.87,
  "statistics": {
    "total_findings": 47,
    "green_count": 38,
    "amber_count": 6,
    "red_count": 3,
    "compliance_rate": 81
  },
  "findings_by_regulation": {
    "Part A - Structure": [...],
    "Part B - Fire Safety": [...],
    "Part L - Energy": [...]
  },
  "cross_discipline_conflicts": [...],
  "priority_actions": [...],
  "agents_executed": ["structural", "fire_safety", ...],
  "processing_time_seconds": 12.4
}
```

---

### 7. Traffic Light Scorer Node
**Purpose**: Applies Green/Amber/Red scoring to all findings and overall document

**Component**: `TrafficLightScorer` (custom component in `langflow/components/traffic_light_scorer.py`)

**Scoring Rules:**
- 🟢 **GREEN**: is_compliant = true AND confidence ≥ 85%
- 🟡 **AMBER**: is_compliant = true AND 70% ≤ confidence < 85% OR is_compliant = false AND confidence < 70%
- 🔴 **RED**: is_compliant = false AND confidence ≥ 70%

**Outputs:**
- All findings with traffic_light_status
- Overall document traffic light status
- Statistics (green_count, amber_count, red_count)

---

### 8. Professional Review Flagging Node
**Purpose**: Flags findings requiring professional engineer review

**Criteria for Mandatory Professional Review:**
- All RED findings
- All AMBER findings
- Buildings > 18m height (Higher-Risk Buildings)
- Structural designs (always require chartered engineer sign-off)
- Fire safety strategies
- Non-standard/innovative solutions

**Outputs:**
- List of findings requiring review
- Recommended professional disciplines (e.g., Chartered Structural Engineer, Fire Engineer)

---

### 9. WYSIWYG Editor Preparation Node
**Purpose**: Formats report for interactive editing in WYSIWYG editor

**Processing:**
- Convert findings to editable document structure
- Add interactive traffic light annotations
- Embed evidence references (page numbers, drawing references)
- Create collaboration placeholders (comments, annotations)
- Format for export (PDF, DOCX)

**Outputs:**
- WYSIWYG editor-ready document
- Interactive elements configuration
- Collaboration settings

---

### 10. Result Storage and Webhook Node
**Purpose**: Stores results in PostgreSQL and returns to FastAPI backend

**Processing:**
- Store in database:
  ```python
  document.ai_analysis = {...}  # Complete AI analysis
  document.compliance_findings = {...}  # Traffic light results
  document.status = DocumentStatus.AI_ANALYSIS_COMPLETE
  ```
- Send webhook to FastAPI:
  ```
  POST /api/v1/langflow/webhook/results
  {
    "document_id": "uuid",
    "overall_status": "amber",
    "findings": [...]
  }
  ```

**Outputs:**
- Database record updated
- Webhook response sent
- User notification triggered

---

## Performance Optimization

### Parallel Processing
- All specialist agents execute in parallel (not sequential)
- Typical processing time: 8-15 seconds for full document analysis

### Caching
- Regulation knowledge base cached (Parts A-P requirements)
- Document classification models cached
- Frequently used calculations cached (U-values, fire resistance)

### Load Balancing
- Distribute agent workload across multiple Langflow instances
- Queue management for high-volume periods

---

## Error Handling

### Agent Failure Recovery
- If one specialist agent fails, continue with others
- Mark failed agent findings as "requires_manual_review"
- Log error for investigation

### Timeout Handling
- Agent timeout: 30 seconds per agent
- Overall workflow timeout: 2 minutes
- Return partial results if timeout occurs

---

## Testing the Master Orchestration

### Test Document 1: Simple Fire Strategy
**Expected**: Fire Safety agent only
**Processing time**: ~5 seconds

### Test Document 2: Full Architectural GA Drawing
**Expected**: All 13 agents invoked
**Processing time**: ~12 seconds

### Test Document 3: Structural Calculations
**Expected**: Structural agent + Building Envelope agent
**Processing time**: ~6 seconds

---

## Integration with FastAPI Backend

**Input Endpoint** (FastAPI → Langflow):
```
POST http://langflow:7860/api/v1/run/master-orchestration
{
  "document_id": "uuid",
  "document_text": "...",
  "user_id": "uuid",
  "tenant_id": "uuid",
  "project_metadata": {...}
}
```

**Output Webhook** (Langflow → FastAPI):
```
POST http://backend:8000/api/v1/langflow/webhook/results
{
  "document_id": "uuid",
  "overall_status": "amber",
  "findings": [...]
}
```

---

## References

All specialist agents must be created and configured before the master orchestration workflow can function. See individual agent READMEs for detailed requirements.

---

**This is the heart of BuiltEnvironment.ai** - the master workflow that coordinates all 13 specialist compliance checking agents to deliver comprehensive, AI-powered building regulations compliance analysis.

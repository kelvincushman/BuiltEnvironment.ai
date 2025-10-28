# Langflow Specialist Compliance Agents

This folder contains the 13 specialist AI agents that analyze building documents for UK Building Regulations compliance. These agents run **within the BuiltEnvironment.ai product** to provide compliance checking services.

## Architecture Overview

```
User uploads document → FastAPI Backend → Langflow Orchestration → 13 Specialist Agents → Compliance Findings → User Dashboard
```

### How It Works

1. **User uploads** building document (PDF, DOCX) via web interface
2. **FastAPI backend** extracts text and sends to Langflow
3. **Master Orchestration** flow classifies document and routes to relevant agents
4. **Specialist Agents** run in parallel to analyze compliance
5. **Results aggregated** and returned to FastAPI
6. **User views** traffic light compliance results (🟢🟡🔴)

---

## The 13 Specialist Agents

### 1. **Fire Safety Agent** (`/flows/fire-safety/`)
- **Regulations**: UK Building Regulations Part B (B1-B5)
- **Standards**: BS 5839, BS 9999, BS EN 12845
- **Analyzes**: Fire safety strategies, detection systems, suppression systems, means of escape

### 2. **Structural Engineering Agent** (`/flows/structural/`)
- **Regulations**: UK Building Regulations Part A
- **Standards**: Eurocodes (BS EN 1990-1999), IStructE
- **Analyzes**: Structural calculations, foundation design, load assessments

### 3. **Building Envelope Agent** (`/flows/building-envelope/`)
- **Regulations**: Parts C (Moisture) & L (Thermal)
- **Standards**: NFRC, GGF, CWCT
- **Analyzes**: Thermal performance, weather protection, glazing safety

### 4. **Mechanical Services Agent** (`/flows/mechanical-services/`)
- **Regulations**: Parts F (Ventilation), G (Water), H (Drainage), J (Combustion)
- **Standards**: CIBSE Guides, HVCA
- **Analyzes**: HVAC systems, plumbing, drainage, energy efficiency

### 5. **Electrical Services Agent** (`/flows/electrical-services/`)
- **Regulations**: Part P (Electrical Safety), Part R (Communications)
- **Standards**: BS 7671 (IET Wiring Regulations)
- **Analyzes**: Electrical installations, low voltage systems, emergency lighting

### 6. **Accessibility Agent** (`/flows/accessibility/`)
- **Regulations**: Part M (Access), Equality Act 2010
- **Standards**: BS 8300
- **Analyzes**: Access provisions, inclusive design, vertical transportation

### 7. **Environmental & Sustainability Agent** (`/flows/environmental-sustainability/`)
- **Regulations**: Part L (Energy), BREEAM, LEED
- **Standards**: MCS, Code for Sustainable Homes
- **Analyzes**: Energy performance, renewable energy, carbon assessments

### 8. **Health & Safety Agent** (`/flows/health-safety/`)
- **Regulations**: CDM 2015, Health & Safety at Work Act
- **Standards**: Control of Asbestos, COSHH
- **Analyzes**: Risk assessments, CDM compliance, method statements

### 9. **Quality Assurance Agent** (`/flows/quality-assurance/`)
- **Regulations**: Construction Products Regulation, BBA
- **Standards**: ATTMA, ISO 9001
- **Analyzes**: Testing procedures, material certifications, commissioning

### 10. **Legal & Contracts Agent** (`/flows/legal-contracts/`)
- **Regulations**: JCT/NEC Contracts, Planning permissions
- **Standards**: Professional indemnity requirements
- **Analyzes**: Contract compliance, warranties, statutory approvals

### 11. **Specialist Systems Agent** (`/flows/specialist-systems/`)
- **Regulations**: LOLER (Lifts), BS EN 81
- **Standards**: BMS, Pool Plant Association
- **Analyzes**: Lifts, escalators, building automation, specialist equipment

### 12. **External Works Agent** (`/flows/external-works/`)
- **Regulations**: SuDS Manual, Highways Act
- **Standards**: Landscape Institute, utility standards
- **Analyzes**: External drainage, landscaping, highway adoptions

### 13. **Finishes & Interiors Agent** (`/flows/finishes-interiors/`)
- **Regulations**: Part E (Acoustics), Part B (Fire for linings)
- **Standards**: Contract Flooring Association
- **Analyzes**: Internal finishes, acoustic performance, fire-rated materials

---

## Folder Structure

```
langflow/
├── README.md                          # This file
├── components/                        # Custom Python components
│   ├── __init__.py
│   ├── base_compliance_agent.py       # Base class for all agents
│   ├── document_classifier.py         # Classify document types
│   ├── traffic_light_scorer.py        # Apply Green/Amber/Red scoring
│   ├── evidence_extractor.py          # Extract quotes from documents
│   ├── regulation_checker.py          # Check against UK regulations
│   └── confidence_calculator.py       # Calculate confidence scores
├── flows/                             # Langflow agent workflows
│   ├── master-orchestration/          # Main routing flow
│   │   ├── master-orchestration.json
│   │   └── README.md
│   ├── fire-safety/                   # Fire Safety agent
│   │   ├── fire-safety-agent.json
│   │   └── README.md
│   ├── structural/                    # Structural agent
│   │   ├── structural-agent.json
│   │   └── README.md
│   └── ... (11 more agents)
└── templates/                         # Reusable templates
    ├── base-agent-template.json       # Template for creating new agents
    └── README.md
```

---

## Custom Python Components

All custom components are in `/components/`. These are reusable building blocks for creating Langflow agents.

### Available Components

1. **BaseComplianceAgent** - Base class with common functionality
2. **DocumentClassifier** - Classify document types (fire safety, structural, etc.)
3. **TrafficLightScorer** - Apply Green/Amber/Red scoring based on confidence
4. **EvidenceExtractor** - Extract relevant quotes and references from documents
5. **RegulationChecker** - Check against specific UK Building Regulations
6. **ConfidenceCalculator** - Calculate confidence scores (0.0-1.0)

### Using Components

In your local Langflow instance:
1. Import the custom component Python file
2. Drag and drop into canvas
3. Connect with other nodes
4. Configure parameters
5. Test with sample documents

---

## Traffic Light System

All agents return findings with traffic light status:

### 🟢 Green (Compliant)
- **Confidence**: >85%
- **Meaning**: Requirement clearly met with strong evidence
- **Example**: "L2 fire alarm system to BS 5839-1:2017 specified"

### 🟡 Amber (Needs Clarification)
- **Confidence**: 70-85%
- **Meaning**: Partially addressed, needs more detail or clarification
- **Example**: "Fire alarm mentioned but category not specified"

### 🔴 Red (Non-Compliant)
- **Confidence**: <70%
- **Meaning**: Requirement not met or missing critical information
- **Example**: "No fire alarm system specified"

---

## JSON Output Format

All agents return findings in this format:

```json
{
  "overall_status": "amber",
  "confidence_score": 0.82,
  "reasoning": "Most Part B requirements addressed but some need clarification",
  "findings": [
    {
      "requirement_id": "B1",
      "requirement_title": "Means of warning and escape",
      "status": "green",
      "confidence": 0.92,
      "evidence": "Document section 3.2 specifies L2 system to BS 5839-1:2017",
      "page_references": [5, 6],
      "issues": [],
      "recommendations": []
    },
    {
      "requirement_id": "B2",
      "requirement_title": "Internal fire spread (linings)",
      "status": "amber",
      "confidence": 0.75,
      "evidence": "Wall linings mentioned as Class 1 but no test certificates",
      "page_references": [12],
      "issues": ["No fire test certificates provided"],
      "recommendations": ["Provide BS 476 test certificates for all wall linings"]
    }
  ],
  "green_count": 15,
  "amber_count": 3,
  "red_count": 1
}
```

---

## Integration with FastAPI Backend

### 1. FastAPI sends document to Langflow

```python
# backend/app/services/langflow_client.py
async def analyze_document(document_id: UUID, document_text: str):
    response = await httpx.post(
        "http://localhost:7860/api/v1/run/master-orchestration",
        json={
            "inputs": {
                "document_text": document_text,
                "tenant_id": str(tenant_id),
                "document_id": str(document_id)
            }
        }
    )
    return response.json()
```

### 2. Langflow processes and returns results

Langflow runs the appropriate specialist agents and returns compliance findings.

### 3. FastAPI stores results

```python
document.compliance_findings = langflow_result
document.status = DocumentStatus.AI_ANALYSIS_COMPLETE
await db.commit()
```

### 4. User views results

User sees traffic light compliance results in the dashboard.

---

## Getting Started

### For Langflow Visual Canvas Setup

1. **Open your local Langflow** (you have this running already)
2. **Import custom components** from `/components/`
3. **Load a flow template** from `/flows/fire-safety/fire-safety-agent.json`
4. **Connect to Claude API** with your Anthropic API key
5. **Test with sample document** text
6. **Export as JSON** and save back to the flow folder
7. **Repeat for all 13 agents**

### For FastAPI Integration

1. **Configure Langflow URL** in `.env`:
   ```
   LANGFLOW_URL=http://localhost:7860
   ```

2. **Create Langflow client** in FastAPI (already created at `backend/app/services/langflow_client.py`)

3. **Call from document processing**:
   ```python
   await langflow_client.analyze_document(document_id, document_text)
   ```

---

## Next Steps

1. ✅ **Agent-OS installed** - Development workflow system set up
2. ✅ **Langflow folder structure created** - All 13 agents have folders
3. ⏳ **Create custom components** - Python components for reusable logic
4. ⏳ **Build Fire Safety agent** - First complete agent in Langflow
5. ⏳ **Build remaining 12 agents** - Complete all specialist agents
6. ⏳ **Test end-to-end** - Document upload → analysis → results
7. ⏳ **Deploy to production** - Docker containers for all services

---

## Support

For questions about:
- **Langflow setup**: See Langflow documentation
- **UK Building Regulations**: See `/docs/compliance/`
- **Agent architecture**: See `/AGENT_ARCHITECTURE.md`
- **FastAPI integration**: See `/backend/README.md`

---

**These are the PRODUCT agents that run WITHIN BuiltEnvironment.ai**

(Separate from the 8 development helper agents in `.claude/agents/`)

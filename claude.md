# Claude Code Integration Guide for BuiltEnvironment.ai

This document provides comprehensive guidance for using Claude Code with the BuiltEnvironment.ai platform.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Slash Commands](#slash-commands)
5. [Skills and Capabilities](#skills-and-capabilities)
6. [Development Workflows](#development-workflows)
7. [AI Agent Architecture](#ai-agent-architecture)
8. [Best Practices](#best-practices)
9. [Integration Points](#integration-points)
10. [Troubleshooting](#troubleshooting)

---

## Overview

BuiltEnvironment.ai is an AI-powered building services consultancy platform that combines Claude AI with experienced building services engineers to transform project design, procurement, and delivery.

### Core Capabilities

- **Multi-Discipline Document Review**: Automated analysis across 13+ building disciplines
- **Compliance Validation**: UK Building Regulations (Parts A-S) and ISO standards checking
- **Traffic Light System**: Visual compliance indicators (Green/Amber/Red)
- **RAG-Powered Chat**: Natural language queries across all project documents
- **Professional Reporting**: Automated generation of compliance and analysis reports

### Technology Stack

- **AI**: Claude (Anthropic), Langflow orchestration, Groq for privacy-focused processing
- **Backend**: FastAPI, PostgreSQL, ChromaDB for vector storage
- **Frontend**: React, Three-panel workspace interface
- **Document Processing**: OCR, PDF extraction, BIM integration (IFC)

---

## Quick Start

### Initial Setup

```bash
# 1. Run the initialization script
./init/setup.sh

# 2. Configure environment variables
cp init/env.example .env
nano .env  # Add your API keys

# 3. Review configuration
nano init/config.yaml

# 4. Verify .claude setup
ls -la .claude/commands
ls -la .claude/skills
```

### First Steps with Claude Code

```bash
# Start Claude Code session
claude-code

# Check available commands
/help

# Try a compliance check
/compliance-check docs/compliance/uk-compliance-architecture.md

# Analyze a document
/analyze-document path/to/building/document.pdf

# Generate a report
/generate-report compliance
```

---

## Project Structure

```
BuiltEnvironment.ai/
├── .claude/                    # Claude Code configuration
│   ├── commands/              # Slash commands
│   ├── skills/                # Reusable capabilities
│   └── README.md              # Configuration docs
│
├── docs/                      # Complete project documentation
│   ├── architecture/          # System architecture
│   ├── business/              # Business planning
│   ├── compliance/            # Regulations & standards
│   ├── implementation/        # Development guides
│   ├── interface/             # UI/UX specifications
│   ├── research/              # Market & technical research
│   └── user-experience/       # User journey & workflows
│
├── init/                      # Initialization & setup
│   ├── setup.sh              # Environment setup script
│   ├── config.yaml           # Base configuration
│   ├── requirements.txt      # Python dependencies
│   └── env.example           # Environment template
│
├── src/                       # Source code (to be created)
├── tests/                     # Test suite (to be created)
├── .env                       # Environment variables (gitignored)
├── README.md                  # Project README
└── claude.md                  # This file
```

---

## Slash Commands

Slash commands provide specialized workflows for common tasks.

### `/compliance-check`

**Purpose**: Analyze documents for UK Building Regulations compliance.

**Usage**:
```
/compliance-check <document_path>
```

**What it does**:
1. Identifies document type and building discipline
2. Extracts key information and specifications
3. Checks against applicable UK Building Regulations (Parts A-S)
4. Applies traffic light system (Green/Amber/Red)
5. Generates detailed findings with regulation references
6. Provides corrective action recommendations

**Example**:
```
/compliance-check docs/architecture/building-specs.pdf

Output:
- Overall Status: 🟡 AMBER (82% confidence)
- Part B (Fire Safety): 🟢 GREEN
- Part L (Energy): 🟡 AMBER (needs clarification on U-values)
- Part M (Accessibility): 🔴 RED (missing DDA compliance details)
```

---

### `/analyze-document`

**Purpose**: Comprehensive multi-discipline analysis of building documents.

**Usage**:
```
/analyze-document <document_path>
```

**What it does**:
1. Classifies document type (drawings, specs, calculations, etc.)
2. Performs discipline-specific analysis:
   - Architectural: Layout, materials, accessibility
   - Structural: Load calculations, material grades
   - Mechanical: HVAC, ventilation, energy performance
   - Electrical: Power distribution, lighting, emergency systems
   - Fire Safety: Fire resistance, escape routes, suppression
3. Cross-discipline coordination review
4. Quality and completeness checks
5. Detailed findings report

**Example**:
```
/analyze-document building-plans/mep-specifications.pdf

Output:
- Document Type: MEP Specifications
- Disciplines: Mechanical, Electrical, Plumbing
- Mechanical Analysis: HVAC system properly sized, efficiency ratings compliant
- Electrical Analysis: Warning - insufficient circuit protection details
- Cross-Discipline: Conflict with structural - duct routing needs coordination
```

---

### `/standards-review`

**Purpose**: Review documents against British Standards and ISO requirements.

**Usage**:
```
/standards-review <document_path>
```

**What it does**:
1. Identifies applicable standards (BS, EN, ISO, CIBSE)
2. Validates technical specifications against standards
3. Checks performance criteria (U-values, acoustic ratings, etc.)
4. Verifies testing and commissioning requirements
5. Generates compliance matrix
6. Prioritizes non-compliances by risk

**Example**:
```
/standards-review electrical-design/circuit-calcs.pdf

Output:
Checking against:
- BS 7671:2018+A2:2022 (Electrical Installations)
- BS EN 60898 (MCB specifications)
- CIBSE Guide M (Maintenance)

Findings:
✓ BS 7671: COMPLIANT - all circuits properly protected
⚠ BS EN 60898: PARTIAL - MCB ratings need verification
✗ CIBSE Guide M: NON-COMPLIANT - maintenance access not specified
```

---

### `/generate-report`

**Purpose**: Create professional compliance and analysis reports.

**Usage**:
```
/generate-report [type] [format]

Types: compliance | technical | standards | status | monthly
Formats: pdf | docx | html | excel | markdown
```

**What it does**:
1. Compiles analysis results from various checks
2. Applies professional report template
3. Generates visual elements (charts, traffic lights, matrices)
4. Structures content with executive summary and details
5. Exports in requested format with branding

**Example**:
```
/generate-report compliance pdf

Output:
Generated: Compliance_Report_2025-10-27_v1.0.pdf
Contents:
- Executive Summary (1 page)
- Overall Status: 🟡 AMBER
- Detailed Findings (15 pages)
- Compliance Matrix (Parts A-S)
- Recommendations (prioritized)
- Action Plan
```

---

### `/review-pr`

**Purpose**: Code review for pull requests.

**Usage**:
```
/review-pr [pr_number]
```

**What it does**:
1. Reviews code for architecture compliance
2. Security analysis (no hardcoded secrets, proper validation)
3. Code quality assessment
4. Testing coverage verification
5. Performance considerations
6. Documentation completeness
7. Provides constructive feedback

**Example**:
```
/review-pr 42

Output:
PR #42: Add multi-tenant dashboard

✓ Architecture: Follows multi-tenant patterns correctly
✓ Security: Proper user ID isolation implemented
⚠ Testing: Coverage at 72% (target: 80%)
⚠ Performance: N+1 query detected in UserController.getProjects()
✓ Documentation: API docs updated

Recommendation: Fix performance issue and add tests before merge.
```

---

## Skills and Capabilities

Skills are reusable capabilities that power the slash commands and can be invoked directly.

### Document Processor

**Purpose**: Document processing, OCR, metadata extraction, content structuring.

**Capabilities**:
- Multi-format support (PDF, DOCX, XLSX, DWG, IFC)
- OCR for scanned documents
- Metadata extraction (project, discipline, revision, date)
- Content classification and tagging
- Quality checks for completeness
- Data structuring for RAG database

**Integration**: Used by all document-related commands.

---

### Compliance Checker

**Purpose**: Automated compliance validation against regulations.

**Capabilities**:
- UK Building Regulations (Parts A-S) validation
- ISO standards checking (9001, 14001, 19650, 45001)
- Traffic light status assignment
- Cross-discipline validation
- Detailed compliance reporting
- Evidence tracking

**Integration**: Powers `/compliance-check` command.

---

### Standards Validator

**Purpose**: Technical validation against British Standards and industry guidelines.

**Capabilities**:
- BS, EN, and CIBSE standards validation
- Performance criteria checking (U-values, acoustics, lighting)
- Material specification validation
- Testing and commissioning requirements
- Version control (checking for superseded standards)
- Compliance matrix generation

**Integration**: Powers `/standards-review` command.

---

### Report Generator

**Purpose**: Professional report creation with multiple format support.

**Capabilities**:
- Multiple report templates (compliance, technical, status, monthly)
- Professional formatting and branding
- Data visualization (charts, graphs, dashboards)
- Multi-format export (PDF, DOCX, HTML, Excel, Markdown)
- Automated sections (TOC, document register, issue tracking)
- Quality assurance checks

**Integration**: Powers `/generate-report` command.

---

### RAG Integrator

**Purpose**: Document indexing and retrieval for RAG-powered chat.

**Capabilities**:
- Intelligent document chunking (structure-aware)
- Vector embedding and indexing
- Real-time knowledge base updates
- Context-aware retrieval
- Multi-document synthesis
- Source attribution and confidence scoring

**Integration**: Supports chat interface and cross-document analysis.

---

## Development Workflows

### Complete Document Review Workflow

```
User uploads building specification document

1. Document Processing
   → Run document-processor skill
   → Extract metadata, OCR if needed, classify content
   → Output: Structured document data

2. Multi-Discipline Analysis
   → /analyze-document command
   → Analyze by discipline (structural, MEP, architectural, etc.)
   → Check cross-discipline coordination
   → Output: Technical analysis report

3. Compliance Check
   → /compliance-check command
   → Validate against UK Building Regulations
   → Apply traffic light system
   → Output: Compliance status with issues

4. Standards Review
   → /standards-review command
   → Check against British Standards
   → Verify performance criteria
   → Output: Standards compliance matrix

5. RAG Integration
   → rag-integrator skill
   → Chunk and embed document
   → Index in vector database
   → Make available for chat queries

6. Report Generation
   → /generate-report compliance
   → Compile all findings
   → Create professional deliverable
   → Output: Client-ready PDF report
```

---

### Code Development Workflow

```
Feature Development Cycle

1. Planning
   → Review architecture docs in /docs/architecture/
   → Check implementation guides in /docs/implementation/
   → Design approach following multi-tenant patterns

2. Implementation
   → Write code following project standards
   → Ensure proper data isolation (user ID based)
   → Integrate with Langflow workflows
   → Implement RAG database connections

3. Self-Review
   → /review-pr command
   → Check for security issues
   → Verify architecture compliance
   → Review test coverage

4. Testing
   → Write unit tests (target: >80% coverage)
   → Integration tests for API endpoints
   → Test multi-tenant isolation
   → Verify RAG integration

5. Documentation
   → Update API documentation
   → Add inline comments for complex logic
   → Update relevant docs in /docs/

6. Commit & Push
   → Commit with descriptive message
   → Push to feature branch
   → Create pull request
   → Team review
```

---

### Compliance Reporting Workflow

```
Monthly Compliance Report Generation

1. Gather Documents
   → Collect all project documents for the period
   → Architectural drawings
   → MEP specifications
   → Structural calculations
   → Fire safety assessments

2. Batch Processing
   → Process all documents through document-processor
   → Run /compliance-check on each document
   → Run /standards-review on technical docs
   → Aggregate results

3. Cross-Analysis
   → Use RAG to identify cross-document conflicts
   → Check for missing dependencies
   → Validate coordination between disciplines

4. Report Generation
   → /generate-report monthly pdf
   → Include period summary
   → Document registry
   → Issues identified and closed
   → Trend analysis
   → Forward look and recommendations

5. Review and Sign-Off
   → Human expert validation (chartered engineer)
   → Address any AI uncertainties
   → Finalize and distribute
```

---

## AI Agent Architecture

BuiltEnvironment.ai uses specialized AI agents for each building discipline.

### Specialized Agents (13 Disciplines)

1. **Structural Engineering Agent**
   - Load calculations validation
   - Material specifications
   - Foundation design
   - Structural integrity

2. **Building Envelope Agent**
   - Thermal performance (U-values)
   - Moisture management
   - Air tightness
   - Weatherproofing

3. **Mechanical Services Agent**
   - HVAC design and sizing
   - Ventilation rates
   - Energy efficiency
   - System specifications

4. **Electrical Systems Agent**
   - Power distribution
   - Lighting design
   - BS 7671 compliance
   - Emergency systems

5. **Fire Safety Agent**
   - Fire resistance ratings
   - Escape route analysis
   - Detection and suppression
   - Compartmentation

6. **Accessibility Agent**
   - Part M compliance
   - Wheelchair access
   - WC facilities
   - Wayfinding

7. **Environmental Sustainability Agent**
   - Part L compliance
   - Energy performance
   - Renewable integration
   - Carbon assessment

8. **Health & Safety Agent**
   - Construction phase planning
   - Risk assessments
   - CDM regulations
   - Safety specifications

9. **Quality Assurance Agent**
   - Documentation completeness
   - Specification consistency
   - Drawing coordination
   - Standard compliance

10. **Legal Compliance Agent**
    - Regulatory requirements
    - Statutory approvals
    - Contract compliance
    - Certification tracking

11. **Specialist Systems Agent**
    - BMS and controls
    - Security systems
    - AV and IT infrastructure
    - Specialist equipment

12. **External Works Agent**
    - Site drainage
    - Landscaping
    - External services
    - Site infrastructure

13. **Finishes Agent**
    - Material specifications
    - Finish schedules
    - Acoustic performance
    - Fire ratings

### Agent Orchestration via Langflow

All agents are orchestrated through Langflow workflows:

```
Document Upload
    ↓
Document Classifier (identifies relevant disciplines)
    ↓
    ├─→ Structural Agent
    ├─→ MEP Agent
    ├─→ Fire Safety Agent
    ├─→ Accessibility Agent
    └─→ [other relevant agents]
    ↓
Results Aggregator
    ↓
Compliance Validator
    ↓
Traffic Light Assigner
    ↓
Report Generator
    ↓
Final Output (with human validation)
```

### Human-AI Collaboration

- AI performs initial analysis (speed and thoroughness)
- Chartered engineers validate findings (expertise and accountability)
- Traffic light system highlights areas needing attention
- 95%+ target accuracy for compliance identification
- Continuous learning from expert feedback

---

## Best Practices

### Document Analysis

**DO:**
- Process documents through the document-processor first
- Run multiple checks (compliance, standards, quality)
- Use RAG integration for cross-document queries
- Generate reports for formal deliverables
- Maintain revision control

**DON'T:**
- Skip metadata extraction
- Ignore cross-discipline conflicts
- Rely solely on AI without expert validation
- Process without understanding document context

### Code Development

**DO:**
- Follow multi-tenant architecture patterns
- Ensure data isolation by user ID
- Write comprehensive tests (>80% coverage)
- Document complex logic
- Use /review-pr before committing
- Follow security best practices

**DON'T:**
- Hard-code credentials or API keys
- Skip input validation
- Ignore N+1 query issues
- Forget GDPR compliance (data retention, user rights)
- Commit without testing

### Compliance Checking

**DO:**
- Check all applicable regulations (Parts A-S)
- Verify against current standards (not superseded)
- Provide specific regulation references
- Prioritize issues by risk/impact
- Track remediation actions

**DON'T:**
- Make assumptions about building classification
- Skip cross-discipline validation
- Ignore amber/yellow flags
- Forget to cite evidence locations
- Overlook Part L energy requirements

### RAG and Chat Integration

**DO:**
- Use context-aware queries
- Cite sources with page numbers
- Provide confidence scores
- Update RAG database when documents change
- Test retrieval relevance

**DON'T:**
- Assume single source has all answers
- Forget to check for document conflicts
- Ignore low-confidence responses
- Skip relationship mapping between docs

---

## Integration Points

### Langflow Integration

Commands and skills integrate with Langflow workflows:

**Configuration**: `/docs/implementation/langflow-workflows-specification.md`

**Key Workflows**:
- `document_processing`: OCR, extraction, classification
- `compliance_check`: Multi-agent compliance validation
- `standards_validation`: Standards checking pipeline

**API Integration**:
```python
# Trigger Langflow workflow from skills
langflow_api_url = os.getenv("LANGFLOW_API_URL")
workflow_id = "compliance_check"

response = requests.post(
    f"{langflow_api_url}/workflows/{workflow_id}/run",
    json={"document_id": doc_id, "user_id": user_id}
)
```

### RAG Database Integration

**Vector Database**: ChromaDB (configured in `/init/config.yaml`)

**Integration Flow**:
```
Document → Chunking → Embedding → Indexing → Available for Chat
```

**Query Flow**:
```
User Question → Query Enhancement → Vector Search + Keyword Search
→ Reranking → Top-K Results → Response Generation → Source Attribution
```

### Multi-Tenant Architecture

**Data Isolation**:
- All database queries filtered by `user_id`
- Document storage segregated by tenant
- RAG collections namespaced by tenant
- Complete audit trails

**Security**:
- JWT authentication
- Role-based access control (RBAC)
- Encryption at rest (AES-256-GCM)
- GDPR compliance (data retention, right to delete)

---

## Troubleshooting

### Commands Not Working

**Issue**: Slash command not recognized
```
Solution:
1. Check .claude/commands/ directory exists
2. Verify command file is present (e.g., compliance-check.md)
3. Ensure file has .md extension
4. Check file permissions (should be readable)
```

**Issue**: Command runs but produces errors
```
Solution:
1. Check document path is correct and accessible
2. Verify file format is supported
3. Review command output for specific error messages
4. Check logs for detailed error traces
```

### Skills Not Available

**Issue**: Skill invocation fails
```
Solution:
1. Verify skill file exists in .claude/skills/
2. Check skill definition is complete
3. Ensure dependencies are installed (see init/requirements.txt)
4. Verify API keys in .env file
```

### RAG Integration Issues

**Issue**: Chat not finding relevant documents
```
Solution:
1. Check documents are properly indexed (run rag-integrator)
2. Verify ChromaDB is running and accessible
3. Check embedding model is configured correctly
4. Review chunk size and overlap settings in config.yaml
5. Test with simpler queries to verify basic functionality
```

**Issue**: Low relevance scores
```
Solution:
1. Adjust similarity_threshold in config.yaml (try 0.6 instead of 0.7)
2. Enable reranking for better results
3. Check if query enhancement is working
4. Verify document metadata is properly tagged
```

### Compliance Check Issues

**Issue**: Incorrect compliance status
```
Solution:
1. Verify building classification is correct
2. Check applicable regulations for building type
3. Review document completeness (missing info → RED status)
4. Validate against current regulations (not outdated)
5. Get expert validation for edge cases
```

### Report Generation Issues

**Issue**: Report formatting problems
```
Solution:
1. Check template files are accessible
2. Verify export format is supported
3. Test with simpler report first (executive summary only)
4. Check for special characters in content
5. Ensure sufficient system resources for PDF generation
```

---

## Additional Resources

### Documentation
- **Business**: `/docs/business/business-plan.md`
- **Architecture**: `/docs/architecture/claude-langflow-architecture.md`
- **Implementation**: `/docs/implementation/expanded-implementation-guide.md`
- **Compliance**: `/docs/compliance/uk-compliance-architecture.md`
- **UI/UX**: `/docs/interface/integrated-workspace-ui-specifications.md`

### Configuration
- **Setup**: `/init/setup.sh`
- **Config**: `/init/config.yaml`
- **Environment**: `/init/env.example`
- **Dependencies**: `/init/requirements.txt`

### Standards Reference
- **Technical Standards**: `/docs/compliance/technical-standards-reference.md`
- **Building Disciplines**: `/docs/compliance/complete-building-disciplines-audit.md`
- **AI Agents Mapping**: `/docs/compliance/ai-agent-discipline-mapping.md`
- **Regulatory Matrix**: `/docs/compliance/regulatory-compliance-matrix.md`

---

## Getting Help

### For Technical Issues
1. Check this guide first
2. Review documentation in `/docs/`
3. Check configuration in `/init/config.yaml`
4. Review error logs
5. Consult implementation guides

### For Compliance Questions
1. Review `/docs/compliance/` documentation
2. Consult technical standards reference
3. Check regulatory compliance matrix
4. Seek chartered engineer validation for critical items

### For Development Questions
1. Review architecture documentation
2. Check implementation guides
3. Use `/review-pr` for code feedback
4. Follow established patterns in codebase

---

## Summary

BuiltEnvironment.ai leverages Claude Code to provide:

✅ **Automated compliance checking** against UK Building Regulations
✅ **Multi-discipline document analysis** across 13+ specializations
✅ **Professional report generation** for client deliverables
✅ **RAG-powered chat** for natural language document queries
✅ **Standards validation** against BS, ISO, and CIBSE guidelines
✅ **Traffic light system** for visual compliance status
✅ **Code review automation** for quality assurance

All powered by specialized AI agents, orchestrated through Langflow, with human expert validation to ensure professional standards and accountability.

---

**Last Updated**: 2025-10-27
**Version**: 1.0.0
**Maintained By**: BuiltEnvironment.ai Development Team

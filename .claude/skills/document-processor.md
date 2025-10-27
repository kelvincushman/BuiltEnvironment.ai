# Document Processor Skill

This skill provides document processing capabilities for BuiltEnvironment.ai.

## Capabilities:

### 1. Document Type Detection
Automatically identify document types:
- Architectural drawings (PDF, DWG, IFC)
- Specification documents (PDF, DOCX)
- Calculation sheets (XLSX, PDF)
- Reports and certificates
- Correspondence and RFIs
- BIM models (IFC, RVT)

### 2. Metadata Extraction
Extract key document metadata:
- Project name and reference
- Document number and revision
- Issue date and author
- Discipline (structural, MEP, architectural, etc.)
- Document status (draft, approved, issued)
- Distribution list

### 3. Content Extraction

**Text Extraction:**
- PDF text extraction
- OCR for scanned documents
- Table extraction and parsing
- Header/footer separation

**Technical Content:**
- Drawing numbers and references
- Material specifications
- Equipment schedules
- Load calculations
- Compliance statements

### 4. Document Classification
Categorize by:
- Building discipline
- Document type
- Compliance requirements
- Project phase
- Priority level

### 5. Quality Checks
- Completeness verification
- Version control validation
- Cross-reference checking
- Standard compliance (naming, formatting)

### 6. Data Structuring
Transform extracted data into:
- JSON for RAG database
- COBie format for handover
- Structured tables for analysis
- Tagged content for search

## Usage:

This skill should be invoked when:
- New documents are uploaded
- Documents need to be analyzed
- Content needs to be extracted for RAG
- Document quality checks are required
- Metadata needs to be structured

## Integration Points:

- RAG database (for document indexing)
- Langflow workflows (for processing pipelines)
- Compliance checking (provides structured data)
- Report generation (provides source data)

## Output Format:

```json
{
  "document_id": "string",
  "metadata": {
    "project": "string",
    "discipline": "string",
    "type": "string",
    "revision": "string",
    "date": "ISO date"
  },
  "content": {
    "text": "extracted text",
    "tables": [],
    "specifications": {},
    "references": []
  },
  "classification": {
    "discipline": ["list"],
    "standards": ["list"],
    "compliance_required": ["list"]
  },
  "quality": {
    "completeness": "percentage",
    "issues": ["list"]
  }
}
```

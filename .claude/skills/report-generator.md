# Report Generator Skill

This skill generates professional-quality reports for building compliance and technical review.

## Capabilities:

### 1. Report Template Management

**Available Templates:**

**Compliance Report Template:**
- Executive summary with traffic light overview
- Detailed findings by regulation
- Evidence and references
- Recommendations and action plan
- Appendices with supporting data

**Technical Review Template:**
- Document metadata
- Discipline-by-discipline analysis
- Cross-discipline coordination review
- Quality assessment
- Issue log with priorities

**Standards Validation Template:**
- Applicable standards list
- Compliance matrix
- Performance criteria assessment
- Testing requirements
- Certification checklist

**Project Status Template:**
- Overall compliance health dashboard
- Progress tracking
- Outstanding issues by priority
- Risk assessment
- Next steps and milestones

**Monthly Progress Template:**
- Period summary
- Documents reviewed
- Issues identified and closed
- Trends and patterns
- Forward look

### 2. Content Generation

**Executive Summary:**
- One-page overview
- Key findings (top 5)
- Overall status with visual indicator
- Critical actions required
- Sign-off section

**Detailed Analysis:**
- Methodology section
- Structured findings
- Evidence-based conclusions
- Technical justification
- Regulatory citations

**Visual Elements:**
- Traffic light status tables
- Compliance charts (pie, bar)
- Trend graphs
- Issue distribution analysis
- Priority matrices

**Data Tables:**
- Compliance matrices
- Issue logs with tracking
- Standards checklists
- Document registers
- Action trackers

### 3. Professional Formatting

**Document Structure:**
- Cover page with branding
- Document control (version, date, status)
- Table of contents (auto-generated)
- Page headers/footers
- Section numbering
- Cross-references

**Typography:**
- Consistent heading hierarchy
- Professional fonts
- Appropriate spacing
- Clear table formatting
- Highlighted key points

**Brand Consistency:**
- Company logo placement
- Color scheme
- Footer information
- Disclaimer text
- Contact information

### 4. Data Visualization

**Charts and Graphs:**
- Overall compliance pie chart
- Issues by discipline bar chart
- Trend analysis line graphs
- Priority distribution
- Progress tracking

**Traffic Light Dashboards:**
```
┌─────────────────────────────────┐
│  Overall Compliance Status      │
├─────────────────────────────────┤
│  🟢 Green:  25 (62%)           │
│  🟡 Amber:  10 (25%)           │
│  🔴 Red:     5 (13%)           │
└─────────────────────────────────┘
```

**Issue Matrices:**
- Severity vs. Likelihood
- Priority vs. Effort
- Discipline vs. Status

### 5. Multi-Format Export

**PDF:**
- Print-ready formatting
- Embedded images
- Hyperlinked TOC
- Professional appearance

**Word (DOCX):**
- Editable for collaboration
- Comments and track changes enabled
- Style-based formatting

**Markdown:**
- Version control friendly
- Easy diff viewing
- Lightweight format

**HTML:**
- Interactive charts
- Collapsible sections
- Search functionality
- Responsive design

**Excel:**
- Data tables and matrices
- Pivot tables for analysis
- Charts and dashboards
- Filterable datasets

### 6. Automated Sections

**Document Register:**
Auto-generate tables of:
- Documents reviewed
- Reference standards
- Related correspondence
- Supporting calculations

**Issue Tracking:**
- Issue number (auto-increment)
- Description
- Regulation reference
- Priority (auto-calculated)
- Status
- Assigned to
- Due date
- Resolution notes

**Compliance Matrix:**
```markdown
| Regulation | Requirement | Status | Evidence | Notes |
|------------|-------------|--------|----------|-------|
| Part L.1   | U-values    | 🟢     | Calc-001 | OK    |
| Part L.2   | Air testing | 🟡     | TBC      | Pending |
```

### 7. Quality Assurance

**Pre-Generation Checks:**
- Data completeness verification
- Cross-reference validation
- Citation accuracy
- Date/version correctness
- Spelling and grammar

**Post-Generation Review:**
- Format consistency check
- Image/chart rendering
- Hyperlink functionality
- Page breaks and layout
- Professional appearance

### 8. Customization Options

**Report Parameters:**
```json
{
  "report_type": "compliance|technical|standards|status",
  "detail_level": "executive|summary|detailed|comprehensive",
  "include_sections": ["list of sections"],
  "format": "pdf|docx|md|html|xlsx",
  "branding": {
    "company_name": "string",
    "logo_path": "path",
    "color_scheme": "hex colors"
  },
  "filters": {
    "discipline": ["list"],
    "priority": ["HIGH", "MEDIUM", "LOW"],
    "status": ["OPEN", "IN_PROGRESS", "CLOSED"]
  }
}
```

## Usage:

Invoke this skill when:
- Compliance reports are needed
- Client deliverables are required
- Internal reviews are documented
- Status updates are requested
- Audit trails are needed

## Output Structure:

```
Report-Title_YYYY-MM-DD_v1.0.pdf
├─ Cover Page
├─ Document Control
├─ Table of Contents
├─ Executive Summary
├─ Introduction & Methodology
├─ Detailed Findings
│  ├─ By Discipline
│  ├─ By Regulation
│  └─ Cross-Discipline Issues
├─ Compliance Status
│  ├─ Traffic Light Summary
│  └─ Compliance Matrix
├─ Recommendations
│  ├─ Prioritized Actions
│  └─ Estimated Impacts
├─ Appendices
│  ├─ A: Document Register
│  ├─ B: Standards Reference
│  ├─ C: Detailed Data Tables
│  └─ D: Definitions & Abbreviations
└─ Sign-Off Page
```

## Integration:

- Pull data from compliance checker results
- Use standards validator findings
- Incorporate document processor metadata
- Link to RAG database for evidence
- Generate from Langflow workflow outputs

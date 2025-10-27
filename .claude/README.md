# Claude Code Configuration

This directory contains Claude Code configuration for BuiltEnvironment.ai development.

## Structure

```
.claude/
├── commands/          # Slash commands for specific workflows
│   ├── compliance-check.md       # Run compliance validation
│   ├── analyze-document.md       # Analyze building documents
│   ├── standards-review.md       # Review against standards
│   ├── generate-report.md        # Generate compliance reports
│   └── review-pr.md              # Code review workflow
│
├── skills/           # Reusable capabilities
│   ├── document-processor.md     # Document processing & OCR
│   ├── compliance-checker.md     # Compliance validation
│   ├── standards-validator.md    # Standards checking
│   ├── report-generator.md       # Report generation
│   └── rag-integrator.md         # RAG database integration
│
└── README.md         # This file
```

## Slash Commands

Slash commands provide specialized workflows for common tasks:

### `/compliance-check`
Analyzes documents for UK Building Regulations compliance and applies the traffic light system.

**Usage:**
```
/compliance-check <document_path>
```

### `/analyze-document`
Performs comprehensive multi-discipline analysis of building documents.

**Usage:**
```
/analyze-document <document_path>
```

### `/standards-review`
Reviews documents against British Standards and ISO requirements.

**Usage:**
```
/standards-review <document_path>
```

### `/generate-report`
Creates professional compliance and analysis reports.

**Usage:**
```
/generate-report [report_type]
```

### `/review-pr`
Reviews pull requests for code quality, security, and architecture compliance.

**Usage:**
```
/review-pr [pr_number]
```

## Skills

Skills are reusable capabilities that can be invoked programmatically:

### Document Processor
Handles document upload, OCR, metadata extraction, and content structuring.

**Key Features:**
- Multi-format support (PDF, DOCX, DWG, IFC)
- Intelligent OCR for scanned documents
- Metadata extraction and classification
- Content structuring for RAG integration

### Compliance Checker
Validates documents against UK Building Regulations (Parts A-S) and ISO standards.

**Key Features:**
- Automatic regulation identification
- Traffic light status assignment
- Cross-discipline validation
- Detailed compliance reporting

### Standards Validator
Checks technical content against British Standards and industry guidelines.

**Key Features:**
- BS, EN, and CIBSE standards validation
- Performance criteria checking
- Material specification validation
- Testing and commissioning requirements

### Report Generator
Generates professional-quality reports with multiple format support.

**Key Features:**
- Multiple report templates
- Traffic light dashboards
- Multi-format export (PDF, DOCX, HTML, Excel)
- Brand customization

### RAG Integrator
Manages document indexing and retrieval for the RAG-powered chat system.

**Key Features:**
- Intelligent document chunking
- Vector embedding and indexing
- Real-time knowledge base updates
- Context-aware retrieval

## Development Workflow

### Document Review Workflow
```
1. Upload document → Document Processor skill
2. Run /analyze-document → Multi-discipline analysis
3. Run /compliance-check → Regulation validation
4. Run /standards-review → Standards checking
5. Run /generate-report → Create deliverable
```

### Code Development Workflow
```
1. Make changes to codebase
2. Run /review-pr → Self-review before commit
3. Address feedback
4. Commit and push
5. Create PR for team review
```

### Compliance Reporting Workflow
```
1. Gather all project documents
2. Process through compliance checker
3. Validate against standards
4. Generate comprehensive report
5. Review and sign off
```

## Configuration

### Environment Setup
Ensure your `.env` file contains necessary API keys:
```bash
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key
```

### Langflow Integration
Commands and skills integrate with Langflow workflows defined in:
- `/docs/implementation/langflow-workflows-specification.md`

### RAG Database
Skills integrate with the vector database configured in:
- `/init/config.yaml`

## Best Practices

### When to Use Slash Commands
- For end-to-end workflows that combine multiple steps
- When you need structured output following a specific process
- For repeatable tasks with consistent methodology

### When to Use Skills
- For reusable capabilities across different workflows
- When building custom automation
- For programmatic integration with other systems

### Adding New Commands/Skills

**New Command:**
1. Create `/home/user/BuiltEnvironment.ai/.claude/commands/your-command.md`
2. Define the workflow and methodology
3. Specify output format
4. Update this README

**New Skill:**
1. Create `/home/user/BuiltEnvironment.ai/.claude/skills/your-skill.md`
2. Define capabilities and interface
3. Specify integration points
4. Update this README

## Troubleshooting

### Commands Not Working
- Ensure the `.md` file exists in the commands directory
- Check for syntax errors in the command file
- Verify file permissions

### Skills Not Available
- Check the skill file exists in skills directory
- Verify the skill definition is complete
- Check for dependency issues

## Reference Documentation

For more information, see:
- `/docs/` - Complete project documentation
- `/init/` - Setup and configuration
- `/claude.md` - Claude Code integration guide

## Support

For issues or questions:
1. Check the documentation in `/docs/`
2. Review configuration in `/init/config.yaml`
3. Consult the implementation guides in `/docs/implementation/`

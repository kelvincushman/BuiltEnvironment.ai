# RAG Integrator Skill

This skill manages the integration of documents into the RAG (Retrieval-Augmented Generation) knowledge base.

## Capabilities:

### 1. Document Chunking Strategy

**Intelligent Chunking:**
- Respect document structure (sections, paragraphs)
- Maintain semantic coherence
- Preserve context across chunks
- Optimal chunk size (1000 tokens default)
- Overlap between chunks (200 tokens)

**Structure-Aware Chunking:**
```
Document → Sections → Subsections → Paragraphs → Chunks
```

**Special Handling:**
- **Tables**: Keep entire table in one chunk if possible
- **Lists**: Group related list items
- **Calculations**: Keep formula + result together
- **Specifications**: Group by specification item
- **Drawings**: Extract text zones logically

### 2. Metadata Enrichment

**Chunk Metadata:**
```json
{
  "chunk_id": "unique_id",
  "document_id": "parent_document",
  "chunk_index": "number",
  "document_metadata": {
    "project": "name",
    "discipline": "structural|MEP|architectural",
    "document_type": "specification|drawing|report",
    "revision": "version",
    "date": "ISO date",
    "author": "name"
  },
  "content_metadata": {
    "section": "section title",
    "heading": "current heading",
    "page_number": "number",
    "contains_table": "boolean",
    "contains_calculation": "boolean",
    "standards_referenced": ["list"],
    "regulations_mentioned": ["list"]
  },
  "semantic_tags": [
    "fire_safety",
    "structural_design",
    "compliance"
  ]
}
```

### 3. Vector Embedding

**Embedding Strategy:**
- Use OpenAI text-embedding-3-small (or alternative)
- Generate embeddings for text chunks
- Store both text and embeddings
- Index for fast similarity search

**Multi-Modal Embeddings:**
- Text embeddings for document content
- Image embeddings for drawings/diagrams
- Table embeddings for structured data

### 4. Knowledge Graph Integration

**Relationship Mapping:**
```
Document A (Structural Calc) ─references→ Document B (Drawing)
Document C (MEP Spec) ─conflicts_with→ Document D (Architectural)
Regulation X ─requires→ Specification Y
Standard A ─supersedes→ Standard B (deprecated)
```

**Entity Extraction:**
- Building elements (beams, columns, ducts)
- Equipment (boilers, pumps, switchgear)
- Regulations and standards
- Measurements and values
- Locations and zones

### 5. Real-Time Updates

**Document Lifecycle:**
```
Upload → Process → Chunk → Embed → Index → Available for Chat
Update → Re-process → Update chunks → Re-embed → Re-index
Delete → Mark inactive → Remove from search (keep audit trail)
```

**Change Detection:**
- Document revision comparison
- Modified sections identification
- Impact assessment on related documents
- Notification of affected analyses

### 6. Query Enhancement

**Context-Aware Retrieval:**
- Use conversation history for context
- Filter by project/discipline
- Boost recent documents
- Prioritize approved revisions

**Hybrid Search:**
- Vector similarity search (semantic)
- Keyword/BM25 search (exact matches)
- Metadata filtering (discipline, type)
- Combined ranking strategy

**Query Rewriting:**
```
User: "What's the U-value for walls?"
Enhanced: "U-value thermal transmittance external walls building fabric insulation Part L"
```

### 7. Response Generation

**Source Attribution:**
- Cite specific documents and sections
- Include page numbers and revision
- Provide confidence scores
- Link to original documents

**Multi-Document Synthesis:**
- Aggregate information from multiple sources
- Identify conflicts between documents
- Provide comprehensive answers
- Maintain source traceability

**Response Format:**
```markdown
Based on the structural calculations (SC-101 Rev B, p.12) and architectural drawings (A-201 Rev C):

The external wall U-value is specified as 0.18 W/m²K, which complies with Part L requirements (max 0.26 W/m²K for new buildings).

**Sources:**
- Thermal Calculations Report (TC-001-RevB.pdf, page 12)
- Building Fabric Specification (Spec-A-001.docx, section 3.2)
- Part L Compliance Statement (Compliance-L.pdf, page 5)

**Confidence:** 95% (HIGH)
```

### 8. Compliance Integration

**Regulation Mapping:**
- Tag chunks with applicable regulations
- Link requirements to evidence
- Track compliance status per chunk
- Enable regulation-specific queries

**Example Query Flows:**
```
Q: "Show me all Part B fire safety requirements"
   → Filter: regulation = "Part B"
   → Retrieve: relevant chunks
   → Generate: compliance checklist

Q: "Are there any conflicts between structural and MEP?"
   → Filter: discipline = ["structural", "MEP"]
   → Analyze: cross-discipline relationships
   → Report: conflicts and dependencies
```

### 9. Performance Optimization

**Caching Strategy:**
- Cache frequent queries
- Pre-compute common relationships
- Materialized views for complex queries
- TTL based on document update frequency

**Indexing:**
- Vector indices (HNSW, IVF)
- Inverted indices for keywords
- Metadata indices for filtering
- Composite indices for common queries

### 10. Quality Assurance

**Ingestion Validation:**
- Verify all chunks embedded
- Check metadata completeness
- Validate relationships
- Test retrieval accuracy

**Monitoring:**
- Query performance metrics
- Retrieval relevance scores
- User feedback on responses
- Coverage analysis (what's not being found)

## Usage:

Invoke this skill when:
- New documents are uploaded
- Documents are updated or revised
- Chat queries need to be processed
- Cross-document analysis is required
- Compliance evidence is needed

## Integration Points:

- Document Processor Skill (receives processed docs)
- Compliance Checker (provides regulation context)
- Standards Validator (links standards references)
- Report Generator (sources evidence and citations)

## Configuration:

```yaml
rag:
  chunk_size: 1000
  chunk_overlap: 200
  embedding_model: "text-embedding-3-small"
  vector_db: "chromadb"
  similarity_threshold: 0.7
  top_k_results: 5
  reranking: true
  cache_ttl: 3600
```

## Output Examples:

**For Chat Query:**
```json
{
  "query": "user question",
  "enhanced_query": "optimized query",
  "retrieved_chunks": [
    {
      "chunk_id": "id",
      "content": "text",
      "metadata": {},
      "similarity_score": 0.92,
      "source": "document reference"
    }
  ],
  "response": "synthesized answer",
  "sources": ["list with full citations"],
  "confidence": 0.95
}
```

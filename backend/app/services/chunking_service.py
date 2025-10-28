"""
Document chunking service for RAG system.

Splits documents into overlapping chunks optimized for embedding and retrieval.
Uses semantic chunking strategies appropriate for building compliance documents.
"""

from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class ChunkingService:
    """
    Service for chunking documents into embedding-ready segments.

    Strategy:
    - Chunk size: 512 tokens (~400 words, ~2000 characters)
    - Overlap: 128 tokens (~100 words, ~500 characters)
    - Preserves paragraph boundaries where possible
    - Maintains section context (headers, page numbers)
    """

    def __init__(
        self,
        chunk_size: int = 2000,  # characters (roughly 512 tokens)
        chunk_overlap: int = 500,  # characters (roughly 128 tokens)
        min_chunk_size: int = 200,  # minimum viable chunk size
    ):
        """
        Initialize chunking service.

        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            min_chunk_size: Minimum chunk size (discard smaller chunks)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk_document(
        self,
        text: str,
        metadata: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Chunk a document into overlapping segments.

        Args:
            text: Full document text
            metadata: Optional metadata to attach to all chunks

        Returns:
            List of chunk dictionaries with:
            - chunk_id: Sequential chunk number
            - text: Chunk text content
            - metadata: Combined metadata (document + chunk-specific)
        """
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided for chunking")
            return []

        # Normalize whitespace
        text = self._normalize_text(text)

        # Split into paragraphs first (preserves semantic boundaries)
        paragraphs = self._split_into_paragraphs(text)

        # Build chunks from paragraphs
        chunks = self._build_chunks_from_paragraphs(paragraphs)

        # Add metadata and IDs
        chunk_dicts = []
        for i, chunk_text in enumerate(chunks):
            chunk_dict = {
                "chunk_id": i,
                "text": chunk_text,
                "metadata": {
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "char_count": len(chunk_text),
                    **(metadata or {}),
                },
            }
            chunk_dicts.append(chunk_dict)

        logger.info(f"Created {len(chunk_dicts)} chunks from {len(text)} characters")
        return chunk_dicts

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for chunking.

        - Remove excessive whitespace
        - Normalize line breaks
        - Preserve meaningful structure
        """
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)

        # Normalize line breaks (max 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove trailing/leading whitespace
        text = text.strip()

        return text

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs.

        Preserves:
        - Natural paragraph breaks (double line breaks)
        - Section headers (detected by patterns)
        - Page markers (from PDF extraction)
        """
        # Split on double line breaks (paragraph boundaries)
        paragraphs = re.split(r'\n\n+', text)

        # Filter empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        return paragraphs

    def _build_chunks_from_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """
        Build chunks from paragraphs, respecting chunk size and overlap.

        Strategy:
        1. Try to keep paragraphs together
        2. If paragraph too large, split it
        3. Add overlap by including last N characters from previous chunk
        """
        chunks = []
        current_chunk = ""
        last_chunk_overlap = ""

        for paragraph in paragraphs:
            # If adding this paragraph exceeds chunk size, save current chunk
            if current_chunk and len(current_chunk) + len(paragraph) > self.chunk_size:
                # Save current chunk
                chunks.append(current_chunk.strip())

                # Start new chunk with overlap
                last_chunk_overlap = self._get_overlap_text(current_chunk)
                current_chunk = last_chunk_overlap

            # If single paragraph exceeds chunk size, split it
            if len(paragraph) > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

                # Split large paragraph into sub-chunks
                sub_chunks = self._split_large_paragraph(paragraph)
                chunks.extend(sub_chunks[:-1])  # Add all but last
                current_chunk = sub_chunks[-1]  # Last becomes current

            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # Add final chunk if exists
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunks.append(current_chunk.strip())

        return chunks

    def _get_overlap_text(self, text: str) -> str:
        """
        Get overlap text from end of chunk.

        Returns last chunk_overlap characters, trying to break at sentence boundary.
        """
        if len(text) <= self.chunk_overlap:
            return text

        # Get last chunk_overlap characters
        overlap_text = text[-self.chunk_overlap:]

        # Try to start at sentence boundary (after period + space)
        sentence_match = re.search(r'\.\s+', overlap_text)
        if sentence_match:
            overlap_text = overlap_text[sentence_match.end():]

        return overlap_text

    def _split_large_paragraph(self, paragraph: str) -> List[str]:
        """
        Split a large paragraph into chunks.

        Uses sentence boundaries where possible.
        """
        chunks = []
        current = ""

        # Try to split on sentences first
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)

        for sentence in sentences:
            if len(current) + len(sentence) > self.chunk_size:
                if current:
                    chunks.append(current.strip())
                    # Add overlap from current
                    current = self._get_overlap_text(current)

                # If single sentence is too large, hard split
                if len(sentence) > self.chunk_size:
                    hard_chunks = self._hard_split_text(sentence)
                    chunks.extend(hard_chunks[:-1])
                    current = hard_chunks[-1]
                else:
                    current += " " + sentence if current else sentence
            else:
                current += " " + sentence if current else sentence

        if current:
            chunks.append(current.strip())

        return chunks

    def _hard_split_text(self, text: str) -> List[str]:
        """
        Hard split text into chunk_size pieces with overlap.

        Used when semantic splitting isn't possible.
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]

            if chunk:
                chunks.append(chunk.strip())

            # Move start forward, accounting for overlap
            start = end - self.chunk_overlap

        return chunks

    def chunk_with_page_context(
        self,
        text: str,
        page_count: int = None,
        metadata: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Chunk a document while preserving page context.

        Assumes text has page markers like "--- Page X ---".

        Args:
            text: Full document text with page markers
            page_count: Total number of pages
            metadata: Optional metadata

        Returns:
            List of chunks with page_number in metadata
        """
        # Split into pages first
        page_pattern = r'\n\n---\s*Page\s+(\d+)\s*---\n\n'
        pages = re.split(page_pattern, text)

        # Pages will be: [text_before_first_marker, page_num_1, page_1_text, page_num_2, page_2_text, ...]
        # Combine them properly
        page_texts = []

        if len(pages) > 1:
            # First element is before any page marker (usually empty or title)
            if pages[0].strip():
                page_texts.append((0, pages[0].strip()))

            # Process pairs of (page_number, page_text)
            for i in range(1, len(pages), 2):
                if i + 1 < len(pages):
                    page_num = int(pages[i])
                    page_text = pages[i + 1].strip()
                    page_texts.append((page_num, page_text))
        else:
            # No page markers, treat as single page
            page_texts.append((1, text))

        # Chunk each page
        all_chunks = []
        global_chunk_id = 0

        for page_num, page_text in page_texts:
            page_metadata = {
                "page_number": page_num,
                **(metadata or {}),
            }

            page_chunks = self.chunk_document(page_text, page_metadata)

            # Update chunk IDs to be global
            for chunk in page_chunks:
                chunk["chunk_id"] = global_chunk_id
                chunk["metadata"]["chunk_index"] = global_chunk_id
                global_chunk_id += 1

            all_chunks.extend(page_chunks)

        logger.info(f"Created {len(all_chunks)} chunks across {len(page_texts)} pages")
        return all_chunks


# Global chunking service instance
chunking_service = ChunkingService()

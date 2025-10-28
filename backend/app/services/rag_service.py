"""
RAG (Retrieval Augmented Generation) service.

Orchestrates document indexing and retrieval for specialist AI agents.
Integrates chunking, embeddings, and vector search.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
import logging

from .chromadb_service import chromadb_service, ChromaDBService
from .chunking_service import chunking_service, ChunkingService

logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG service for document indexing and retrieval.

    Workflow:
    1. Document Upload → Index
       - Extract text
       - Chunk document
       - Generate embeddings (via ChromaDB + OpenAI)
       - Store in collections for relevant agents

    2. Agent Query → Retrieve
       - Agent specifies query and domain
       - Retrieve relevant chunks from agent's collection
       - Return context for LLM analysis
    """

    def __init__(
        self,
        chroma_service: ChromaDBService = chromadb_service,
        chunking_service_instance: ChunkingService = chunking_service,
    ):
        """Initialize RAG service with dependencies."""
        self.chroma = chroma_service
        self.chunker = chunking_service_instance

    async def initialize(self):
        """Initialize RAG service (connect to ChromaDB)."""
        await self.chroma.connect()
        logger.info("RAG service initialized")

    async def shutdown(self):
        """Shutdown RAG service (disconnect from ChromaDB)."""
        await self.chroma.disconnect()
        logger.info("RAG service shutdown")

    async def index_document(
        self,
        document_id: UUID,
        tenant_id: UUID,
        project_id: UUID,
        text: str,
        page_count: Optional[int] = None,
        document_metadata: Optional[Dict[str, Any]] = None,
        agent_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Index a document for RAG retrieval.

        Args:
            document_id: Document UUID
            tenant_id: Tenant UUID
            project_id: Project UUID
            text: Extracted document text
            page_count: Number of pages (for page context)
            document_metadata: Document metadata (filename, type, etc.)
            agent_names: List of specialist agents to index for
                        If None, indexes for all agents

        Returns:
            Dictionary with indexing statistics
        """
        if not text or len(text.strip()) == 0:
            logger.warning(f"Empty text for document {document_id}, skipping indexing")
            return {
                "document_id": str(document_id),
                "status": "skipped",
                "reason": "empty_text",
            }

        # Prepare metadata
        metadata = {
            "document_id": str(document_id),
            "tenant_id": str(tenant_id),
            "project_id": str(project_id),
            **(document_metadata or {}),
        }

        # Chunk document
        if page_count and page_count > 1:
            chunks = self.chunker.chunk_with_page_context(
                text=text,
                page_count=page_count,
                metadata=metadata,
            )
        else:
            chunks = self.chunker.chunk_document(
                text=text,
                metadata=metadata,
            )

        if not chunks:
            logger.warning(f"No chunks created for document {document_id}")
            return {
                "document_id": str(document_id),
                "status": "failed",
                "reason": "no_chunks_created",
            }

        # Determine which agents to index for
        if agent_names is None:
            # Index for all specialist agents + general
            agent_names = ChromaDBService.SPECIALIST_AGENTS + ["general"]
        else:
            # Validate agent names
            valid_agents = ChromaDBService.SPECIALIST_AGENTS + ["general"]
            agent_names = [a for a in agent_names if a in valid_agents]

        # Index chunks for each agent
        indexing_results = {}

        for agent_name in agent_names:
            try:
                chunks_added = await self.chroma.add_document_chunks(
                    agent_name=agent_name,
                    chunks=chunks,
                    tenant_id=tenant_id,
                    document_id=document_id,
                    project_id=project_id,
                )

                indexing_results[agent_name] = {
                    "status": "success",
                    "chunks_added": chunks_added,
                }

            except Exception as e:
                logger.error(f"Failed to index for {agent_name}: {e}")
                indexing_results[agent_name] = {
                    "status": "failed",
                    "error": str(e),
                }

        # Calculate overall statistics
        total_chunks = len(chunks)
        successful_agents = sum(1 for r in indexing_results.values() if r["status"] == "success")

        return {
            "document_id": str(document_id),
            "status": "completed",
            "total_chunks": total_chunks,
            "agents_indexed": successful_agents,
            "agent_results": indexing_results,
        }

    async def query_for_context(
        self,
        query: str,
        agent_name: str,
        tenant_id: UUID,
        n_results: int = 5,
        document_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query for relevant document chunks (RAG context).

        Args:
            query: Search query (natural language)
            agent_name: Specialist agent name (e.g., "fire_safety")
            tenant_id: Tenant UUID (for isolation)
            n_results: Number of chunks to retrieve
            document_id: Optional filter by document
            project_id: Optional filter by project

        Returns:
            List of relevant chunks with metadata
        """
        try:
            results = await self.chroma.query_agent_collection(
                agent_name=agent_name,
                query_text=query,
                tenant_id=tenant_id,
                n_results=n_results,
                document_id=document_id,
                project_id=project_id,
            )

            logger.info(f"Retrieved {len(results)} chunks for {agent_name} query")
            return results

        except Exception as e:
            logger.error(f"Failed to query {agent_name}: {e}")
            return []

    async def delete_document_from_index(
        self,
        document_id: UUID,
        tenant_id: UUID,
    ) -> Dict[str, Any]:
        """
        Delete all chunks for a document from all collections.

        Args:
            document_id: Document UUID
            tenant_id: Tenant UUID

        Returns:
            Deletion statistics
        """
        try:
            chunks_deleted = await self.chroma.delete_document_chunks(
                tenant_id=tenant_id,
                document_id=document_id,
            )

            logger.info(f"Deleted {chunks_deleted} chunks for document {document_id}")

            return {
                "document_id": str(document_id),
                "status": "success",
                "chunks_deleted": chunks_deleted,
            }

        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return {
                "document_id": str(document_id),
                "status": "failed",
                "error": str(e),
            }

    async def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specialist agent's collection.

        Args:
            agent_name: Specialist agent name

        Returns:
            Collection statistics
        """
        try:
            stats = await self.chroma.get_collection_stats(agent_name)
            return stats

        except Exception as e:
            logger.error(f"Failed to get stats for {agent_name}: {e}")
            return {
                "agent_name": agent_name,
                "status": "error",
                "error": str(e),
            }

    async def reindex_document(
        self,
        document_id: UUID,
        tenant_id: UUID,
        project_id: UUID,
        text: str,
        page_count: Optional[int] = None,
        document_metadata: Optional[Dict[str, Any]] = None,
        agent_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Reindex a document (delete old chunks, index new ones).

        Useful when document content changes or agents need updating.

        Args:
            Same as index_document

        Returns:
            Reindexing statistics
        """
        # Delete existing chunks
        delete_result = await self.delete_document_from_index(
            document_id=document_id,
            tenant_id=tenant_id,
        )

        # Index document
        index_result = await self.index_document(
            document_id=document_id,
            tenant_id=tenant_id,
            project_id=project_id,
            text=text,
            page_count=page_count,
            document_metadata=document_metadata,
            agent_names=agent_names,
        )

        return {
            "document_id": str(document_id),
            "status": "completed",
            "deleted": delete_result,
            "indexed": index_result,
        }

    def format_context_for_llm(
        self,
        chunks: List[Dict[str, Any]],
        max_chunks: int = 5,
    ) -> str:
        """
        Format retrieved chunks into context string for LLM.

        Args:
            chunks: List of chunk dictionaries from query_for_context
            max_chunks: Maximum chunks to include

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found."

        context_parts = ["# Relevant Document Context\n"]

        for i, chunk in enumerate(chunks[:max_chunks]):
            context_parts.append(f"\n## Chunk {i + 1}")

            # Add metadata if available
            metadata = chunk.get("metadata", {})
            if "page_number" in metadata:
                context_parts.append(f"(Page {metadata['page_number']})")

            # Add chunk text
            context_parts.append(f"\n{chunk['text']}\n")

            # Add separator
            context_parts.append("---")

        return "\n".join(context_parts)


# Global RAG service instance
rag_service = RAGService()

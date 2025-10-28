"""
ChromaDB service for vector storage and retrieval.

Creates separate collections for each of the 13 specialist compliance agents,
enabling targeted RAG queries for domain-specific compliance checking.
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional, Any
from uuid import UUID
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


class ChromaDBService:
    """
    Service for managing ChromaDB vector storage.

    Architecture:
    - One collection per specialist agent (13 total)
    - One collection for general/cross-agent queries
    - Collections are tenant-scoped via metadata filtering
    - Uses OpenAI embeddings (text-embedding-3-small)
    """

    # The 13 specialist compliance agents
    SPECIALIST_AGENTS = [
        "structural_engineering",      # Part A, Eurocodes
        "building_envelope",           # Parts C & L, thermal
        "mechanical_services",         # Parts F, G, H, J (HVAC, plumbing)
        "electrical_services",         # Part P, BS 7671
        "fire_safety",                 # Part B (B1-B5)
        "accessibility",               # Part M, BS 8300
        "environmental_sustainability",# Part L, BREEAM, LEED
        "health_safety",               # CDM 2015
        "quality_assurance",           # Testing, commissioning
        "legal_contracts",             # Contracts, warranties
        "specialist_systems",          # Lifts, BMS
        "external_works",              # Drainage, landscaping
        "finishes_interiors",          # Part E (acoustics), finishes
    ]

    def __init__(self):
        """Initialize ChromaDB client and embedding function."""
        self.client = None
        self.embedding_function = None
        self._collections = {}

    async def connect(self):
        """Connect to ChromaDB instance."""
        if self.client is not None:
            return

        try:
            # Connect to ChromaDB
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=Settings(
                    anonymized_telemetry=False,
                ),
            )

            # Initialize OpenAI embedding function
            self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name="text-embedding-3-small",  # 1536 dimensions, $0.02/1M tokens
            )

            # Create collections for each specialist agent
            await self._initialize_collections()

            logger.info("ChromaDB connection established")

        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise

    async def _initialize_collections(self):
        """
        Initialize collections for all specialist agents.

        Each collection stores document chunks for a specific compliance domain,
        enabling targeted RAG queries for specialist agents.
        """
        # Create collection for each specialist agent
        for agent_name in self.SPECIALIST_AGENTS:
            collection_name = f"agent_{agent_name}"

            try:
                collection = self.client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function,
                    metadata={
                        "agent": agent_name,
                        "description": f"Document chunks for {agent_name} agent",
                    }
                )
                self._collections[agent_name] = collection
                logger.info(f"Initialized collection: {collection_name}")

            except Exception as e:
                logger.error(f"Failed to create collection {collection_name}: {e}")
                raise

        # Create general collection for cross-agent queries
        try:
            general_collection = self.client.get_or_create_collection(
                name="agent_general",
                embedding_function=self.embedding_function,
                metadata={
                    "agent": "general",
                    "description": "General document chunks for cross-agent queries",
                }
            )
            self._collections["general"] = general_collection
            logger.info("Initialized collection: agent_general")

        except Exception as e:
            logger.error(f"Failed to create general collection: {e}")
            raise

    async def disconnect(self):
        """Disconnect from ChromaDB."""
        self.client = None
        self._collections = {}
        logger.info("ChromaDB connection closed")

    async def add_document_chunks(
        self,
        agent_name: str,
        chunks: List[Dict[str, Any]],
        tenant_id: UUID,
        document_id: UUID,
        project_id: UUID,
    ) -> int:
        """
        Add document chunks to a specialist agent's collection.

        Args:
            agent_name: Name of the specialist agent (e.g., "fire_safety")
            chunks: List of chunk dictionaries with 'text', 'metadata', and 'chunk_id'
            tenant_id: Tenant UUID for multi-tenant isolation
            document_id: Document UUID
            project_id: Project UUID

        Returns:
            Number of chunks added
        """
        if agent_name not in self._collections:
            raise ValueError(f"Unknown agent: {agent_name}")

        collection = self._collections[agent_name]

        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            # Create unique ID: {tenant_id}_{document_id}_{chunk_id}
            chunk_id = f"{tenant_id}_{document_id}_{chunk['chunk_id']}"
            ids.append(chunk_id)
            documents.append(chunk["text"])

            # Merge chunk metadata with tenant/document info
            metadata = {
                "tenant_id": str(tenant_id),
                "document_id": str(document_id),
                "project_id": str(project_id),
                "chunk_index": chunk["chunk_id"],
                **chunk.get("metadata", {}),
            }
            metadatas.append(metadata)

        # Add to collection
        try:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
            logger.info(f"Added {len(chunks)} chunks to {agent_name} collection")
            return len(chunks)

        except Exception as e:
            logger.error(f"Failed to add chunks to {agent_name}: {e}")
            raise

    async def query_agent_collection(
        self,
        agent_name: str,
        query_text: str,
        tenant_id: UUID,
        n_results: int = 5,
        document_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query a specialist agent's collection for relevant document chunks.

        Args:
            agent_name: Name of the specialist agent
            query_text: Query text to search for
            tenant_id: Tenant UUID (required for multi-tenant isolation)
            n_results: Number of results to return
            document_id: Optional filter by specific document
            project_id: Optional filter by specific project

        Returns:
            List of matching chunks with text, metadata, and distance
        """
        if agent_name not in self._collections:
            raise ValueError(f"Unknown agent: {agent_name}")

        collection = self._collections[agent_name]

        # Build where clause for filtering
        where = {"tenant_id": str(tenant_id)}

        if document_id:
            where["document_id"] = str(document_id)

        if project_id:
            where["project_id"] = str(project_id)

        # Query collection
        try:
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
            )

            # Format results
            formatted_results = []

            if results["ids"] and len(results["ids"]) > 0:
                for i in range(len(results["ids"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None,
                    })

            logger.info(f"Query returned {len(formatted_results)} results from {agent_name}")
            return formatted_results

        except Exception as e:
            logger.error(f"Failed to query {agent_name}: {e}")
            raise

    async def delete_document_chunks(
        self,
        tenant_id: UUID,
        document_id: UUID,
    ) -> int:
        """
        Delete all chunks for a document across all collections.

        Args:
            tenant_id: Tenant UUID
            document_id: Document UUID

        Returns:
            Total number of chunks deleted
        """
        total_deleted = 0

        for agent_name, collection in self._collections.items():
            try:
                # ChromaDB requires deleting by ID pattern
                # Get all IDs matching this document
                where = {
                    "tenant_id": str(tenant_id),
                    "document_id": str(document_id),
                }

                # Query to get IDs to delete
                results = collection.get(where=where)

                if results["ids"]:
                    collection.delete(ids=results["ids"])
                    deleted_count = len(results["ids"])
                    total_deleted += deleted_count
                    logger.info(f"Deleted {deleted_count} chunks from {agent_name}")

            except Exception as e:
                logger.error(f"Failed to delete chunks from {agent_name}: {e}")
                # Continue with other collections

        logger.info(f"Total chunks deleted: {total_deleted}")
        return total_deleted

    async def get_collection_stats(self, agent_name: str) -> Dict[str, Any]:
        """
        Get statistics for a collection.

        Args:
            agent_name: Name of the specialist agent

        Returns:
            Dictionary with collection statistics
        """
        if agent_name not in self._collections:
            raise ValueError(f"Unknown agent: {agent_name}")

        collection = self._collections[agent_name]

        try:
            count = collection.count()

            return {
                "agent_name": agent_name,
                "total_chunks": count,
                "collection_name": f"agent_{agent_name}",
            }

        except Exception as e:
            logger.error(f"Failed to get stats for {agent_name}: {e}")
            raise


# Global ChromaDB service instance
chromadb_service = ChromaDBService()

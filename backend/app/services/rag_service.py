"""
RAG (Retrieval Augmented Generation) service using ChromaDB.
Handles document indexing, embedding, and context retrieval for AI agents.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import openai

from ..core.config import settings


class RAGService:
    """
    Service for document embedding and retrieval using ChromaDB.
    Each tenant has their own isolated collection.
    """

    def __init__(self):
        """Initialize ChromaDB client and OpenAI embeddings."""
        # Initialize ChromaDB client
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )

        # Use OpenAI embeddings (text-embedding-3-small is fast and cost-effective)
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.OPENAI_API_KEY,
            model_name="text-embedding-3-small",
        )

    def get_or_create_collection(self, tenant_id: str) -> chromadb.Collection:
        """
        Get or create a collection for a tenant.
        Each tenant has isolated data in their own collection.
        """
        collection_name = f"tenant_{tenant_id.replace('-', '_')}"

        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
            )
        except Exception:
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"tenant_id": tenant_id},
            )

        return collection

    def index_document(
        self,
        tenant_id: str,
        document_id: str,
        chunks: List[Dict[str, Any]],
        document_metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Index document chunks into ChromaDB.

        Args:
            tenant_id: Tenant ID for collection isolation
            document_id: Document UUID
            chunks: List of text chunks with metadata
            document_metadata: Document-level metadata (filename, type, etc.)

        Returns:
            Indexing result with stats
        """
        collection = self.get_or_create_collection(tenant_id)

        # Prepare data for ChromaDB
        ids = []
        texts = []
        metadatas = []

        for chunk in chunks:
            chunk_id = f"{document_id}_chunk_{chunk['chunk_index']}"
            ids.append(chunk_id)
            texts.append(chunk["text"])

            # Combine document metadata with chunk metadata
            chunk_metadata = {
                "document_id": document_id,
                "chunk_index": chunk["chunk_index"],
                "start_char": chunk["start_char"],
                "end_char": chunk["end_char"],
                **document_metadata,
            }
            metadatas.append(chunk_metadata)

        # Add to collection
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
        )

        return {
            "collection_id": collection.name,
            "chunk_count": len(chunks),
            "document_id": document_id,
        }

    def search(
        self,
        tenant_id: str,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks.

        Args:
            tenant_id: Tenant ID for collection isolation
            query: Search query
            n_results: Number of results to return
            filters: Optional metadata filters (e.g., {"document_id": "uuid"})

        Returns:
            List of relevant chunks with metadata and distances
        """
        collection = self.get_or_create_collection(tenant_id)

        # Build where clause for filtering
        where_clause = filters if filters else None

        # Search
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause,
        )

        # Format results
        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                formatted_results.append({
                    "chunk_id": chunk_id,
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                })

        return formatted_results

    def delete_document(self, tenant_id: str, document_id: str) -> None:
        """
        Delete all chunks for a document from the collection.

        Args:
            tenant_id: Tenant ID
            document_id: Document UUID to delete
        """
        collection = self.get_or_create_collection(tenant_id)

        # Delete all chunks for this document
        try:
            collection.delete(
                where={"document_id": document_id}
            )
        except Exception as e:
            print(f"Error deleting document chunks: {str(e)}")

    def get_collection_stats(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get statistics for a tenant's collection.

        Returns:
            {
                "total_chunks": int,
                "total_documents": int,
                "collection_name": str
            }
        """
        collection = self.get_or_create_collection(tenant_id)

        # Get all items to calculate stats
        try:
            count = collection.count()

            # Get unique document IDs
            results = collection.get()
            unique_docs = set()
            if results["metadatas"]:
                unique_docs = {
                    meta.get("document_id")
                    for meta in results["metadatas"]
                    if meta.get("document_id")
                }

            return {
                "total_chunks": count,
                "total_documents": len(unique_docs),
                "collection_name": collection.name,
            }
        except Exception as e:
            return {
                "total_chunks": 0,
                "total_documents": 0,
                "collection_name": collection.name,
                "error": str(e),
            }


class ChatService:
    """
    Service for RAG-powered chat using retrieved context.
    """

    def __init__(self, rag_service: RAGService):
        """Initialize with RAG service."""
        self.rag_service = rag_service

    async def generate_response(
        self,
        tenant_id: str,
        user_query: str,
        document_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate AI response using RAG context.

        Args:
            tenant_id: Tenant ID
            user_query: User's question
            document_id: Optional document ID to limit context to specific document
            conversation_history: Previous messages for context

        Returns:
            {
                "response": "AI generated response",
                "sources": ["chunk1", "chunk2"],
                "metadata": {...}
            }
        """

        # Search for relevant context
        filters = {"document_id": document_id} if document_id else None
        relevant_chunks = self.rag_service.search(
            tenant_id=tenant_id,
            query=user_query,
            n_results=5,
            filters=filters,
        )

        # Build context from retrieved chunks
        context_parts = []
        sources = []

        for i, chunk in enumerate(relevant_chunks):
            context_parts.append(f"[Context {i+1}]\n{chunk['text']}\n")
            sources.append({
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["metadata"].get("document_id"),
                "filename": chunk["metadata"].get("filename"),
                "relevance_score": 1 - (chunk["distance"] or 0),  # Convert distance to similarity
            })

        context = "\n".join(context_parts)

        # Build conversation history
        messages = []

        # System message
        system_message = f"""You are an AI assistant for BuiltEnvironment.ai, helping analyze building documents and check compliance with UK Building Regulations.

Use the following context from the uploaded documents to answer the user's question:

{context}

Guidelines:
- Cite specific document sections when making claims
- If the context doesn't contain the answer, say so clearly
- For compliance questions, reference specific regulations (Part A-S)
- Be precise and technical when discussing building standards
- If asked about fire safety, reference Part B specifically"""

        messages.append({"role": "system", "content": system_message})

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user query
        messages.append({"role": "user", "content": user_query})

        # Generate response using Anthropic Claude
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=messages,
            )

            ai_response = response.content[0].text

            return {
                "response": ai_response,
                "sources": sources,
                "metadata": {
                    "model": "claude-3-5-sonnet-20241022",
                    "chunks_used": len(relevant_chunks),
                    "tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
            }

        except Exception as e:
            return {
                "response": f"Error generating response: {str(e)}",
                "sources": sources,
                "metadata": {"error": str(e)},
            }

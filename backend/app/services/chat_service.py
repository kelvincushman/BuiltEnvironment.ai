"""
Chat service for AI-powered document conversations.

Integrates:
- RAG system for context retrieval
- Specialist agent selection
- Claude AI for responses
- Conversation history management
"""

from typing import List, Dict, Any, Optional, AsyncIterator
from uuid import UUID
import logging
from anthropic import AsyncAnthropic

from ..core.config import settings
from .rag_service import rag_service
from .chromadb_service import ChromaDBService

logger = logging.getLogger(__name__)


class ChatService:
    """
    Service for RAG-powered chat with specialist AI agents.

    Features:
    - Context-aware responses using RAG
    - Specialist agent system prompts
    - Streaming support
    - Citation of source documents
    """

    # Specialist agent configurations
    SPECIALIST_AGENTS = {
        "general": {
            "name": "General Compliance Assistant",
            "description": "General building compliance and documentation support",
            "uk_building_parts": ["All Parts"],
            "specialties": ["General compliance", "Cross-discipline coordination"],
            "system_prompt": """You are a general building compliance assistant for BuiltEnvironment.ai.
You help users understand UK Building Regulations and analyze their construction documents.

When answering:
- Reference specific UK Building Regulations parts (A-S) when relevant
- Cite document sections and page numbers from the provided context
- Be precise and technical with building standards
- Suggest which specialist agents might help with specific questions""",
        },
        "structural_engineering": {
            "name": "Structural Engineering Agent",
            "description": "Structural design and Part A compliance",
            "uk_building_parts": ["Part A - Structure", "Eurocodes"],
            "specialties": ["Structural design", "Load calculations", "Eurocode compliance"],
            "system_prompt": """You are a structural engineering specialist for BuiltEnvironment.ai.
You analyze structural designs for compliance with Part A of UK Building Regulations and Eurocodes.

Focus on:
- Structural integrity and stability
- Load-bearing calculations
- Foundation design
- Material specifications
- Part A compliance requirements
- Eurocode standards (BS EN 1990-1999)

Always reference specific regulation clauses and Eurocode sections when providing guidance.""",
        },
        "fire_safety": {
            "name": "Fire Safety Agent",
            "description": "Fire safety strategy and Part B compliance",
            "uk_building_parts": ["Part B - Fire Safety (B1-B5)"],
            "specialties": ["Fire safety design", "Means of escape", "Fire resistance", "Compartmentation"],
            "system_prompt": """You are a fire safety specialist for BuiltEnvironment.ai.
You analyze fire safety strategies for compliance with Part B of UK Building Regulations.

Focus on:
- Part B1: Means of warning and escape
- Part B2: Internal fire spread (linings)
- Part B3: Internal fire spread (structure)
- Part B4: External fire spread
- Part B5: Access and facilities for the fire service
- Fire resistance periods
- Compartmentation requirements
- Travel distances and escape routes

Always cite specific Part B clauses and approved document guidance.""",
        },
        "accessibility": {
            "name": "Accessibility Agent",
            "description": "Accessible design and Part M compliance",
            "uk_building_parts": ["Part M - Access", "BS 8300"],
            "specialties": ["Accessible design", "Inclusive design", "Wheelchair access"],
            "system_prompt": """You are an accessibility specialist for BuiltEnvironment.ai.
You analyze designs for compliance with Part M of UK Building Regulations and BS 8300.

Focus on:
- Part M compliance for all building types
- BS 8300 best practice
- Accessible approach and entrance
- Vertical and horizontal circulation
- WC provision and design
- Accessible parking
- Wayfinding and signage

Ensure inclusive design principles are met beyond minimum compliance.""",
        },
        # Add more specialist agents as needed...
    }

    def __init__(self):
        """Initialize chat service."""
        self.anthropic = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    def get_specialist_agents(self) -> List[Dict[str, Any]]:
        """
        Get list of available specialist agents.

        Returns:
            List of agent configurations
        """
        return [
            {
                "agent_id": agent_id,
                **config
            }
            for agent_id, config in self.SPECIALIST_AGENTS.items()
        ]

    def _get_system_prompt(self, agent_id: str) -> str:
        """
        Get system prompt for a specialist agent.

        Args:
            agent_id: Specialist agent identifier

        Returns:
            System prompt string
        """
        agent_config = self.SPECIALIST_AGENTS.get(agent_id, self.SPECIALIST_AGENTS["general"])
        return agent_config["system_prompt"]

    async def generate_response(
        self,
        user_message: str,
        tenant_id: UUID,
        project_id: UUID,
        specialist_agent: str = "general",
        document_ids: Optional[List[UUID]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate AI response using RAG context.

        Args:
            user_message: User's question/message
            tenant_id: Tenant UUID
            project_id: Project UUID
            specialist_agent: Which specialist agent to use
            document_ids: Optional specific documents to query
            conversation_history: Previous messages for context

        Returns:
            Dictionary with response and metadata:
            {
                "content": "AI response text",
                "rag_context": {...},
                "ai_metadata": {...}
            }
        """
        # Retrieve relevant context from RAG
        rag_context = await self._retrieve_rag_context(
            query=user_message,
            agent_id=specialist_agent,
            tenant_id=tenant_id,
            project_id=project_id,
            document_ids=document_ids,
        )

        # Build messages for Claude
        messages = []

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user message with RAG context
        user_message_with_context = self._format_user_message_with_context(
            user_message=user_message,
            rag_context=rag_context,
        )
        messages.append({
            "role": "user",
            "content": user_message_with_context
        })

        # Get system prompt for specialist agent
        system_prompt = self._get_system_prompt(specialist_agent)

        # Generate response with Claude
        try:
            response = await self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.7,
                system=system_prompt,
                messages=messages,
            )

            ai_response = response.content[0].text

            # Prepare metadata
            ai_metadata = {
                "model": "claude-3-5-sonnet-20241022",
                "tokens_input": response.usage.input_tokens,
                "tokens_output": response.usage.output_tokens,
                "temperature": 0.7,
                "specialist_agent": specialist_agent,
            }

            return {
                "content": ai_response,
                "rag_context": rag_context,
                "ai_metadata": ai_metadata,
            }

        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            raise

    async def generate_response_stream(
        self,
        user_message: str,
        tenant_id: UUID,
        project_id: UUID,
        specialist_agent: str = "general",
        document_ids: Optional[List[UUID]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> AsyncIterator[str]:
        """
        Generate streaming AI response using RAG context.

        Args:
            Same as generate_response

        Yields:
            Text chunks as they are generated
        """
        # Retrieve RAG context
        rag_context = await self._retrieve_rag_context(
            query=user_message,
            agent_id=specialist_agent,
            tenant_id=tenant_id,
            project_id=project_id,
            document_ids=document_ids,
        )

        # Build messages
        messages = []
        if conversation_history:
            messages.extend(conversation_history)

        user_message_with_context = self._format_user_message_with_context(
            user_message=user_message,
            rag_context=rag_context,
        )
        messages.append({
            "role": "user",
            "content": user_message_with_context
        })

        # Get system prompt
        system_prompt = self._get_system_prompt(specialist_agent)

        # Stream response
        try:
            async with self.anthropic.messages.stream(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.7,
                system=system_prompt,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Failed to stream AI response: {e}")
            raise

    async def _retrieve_rag_context(
        self,
        query: str,
        agent_id: str,
        tenant_id: UUID,
        project_id: UUID,
        document_ids: Optional[List[UUID]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve relevant document chunks using RAG.

        Args:
            query: User's question
            agent_id: Specialist agent ID
            tenant_id: Tenant UUID
            project_id: Project UUID
            document_ids: Optional specific documents to search

        Returns:
            RAG context dictionary
        """
        try:
            # Query the appropriate specialist agent collection
            chunks = await rag_service.query_for_context(
                query=query,
                agent_name=agent_id,
                tenant_id=tenant_id,
                project_id=project_id,
                n_results=5,  # Retrieve top 5 most relevant chunks
            )

            # Filter by specific documents if requested
            if document_ids:
                document_id_strings = [str(doc_id) for doc_id in document_ids]
                chunks = [
                    chunk for chunk in chunks
                    if chunk.get("metadata", {}).get("document_id") in document_id_strings
                ]

            # Format context summary
            return {
                "agent": agent_id,
                "chunks_retrieved": len(chunks),
                "chunks": chunks,
                "sources": self._extract_sources(chunks),
            }

        except Exception as e:
            logger.error(f"Failed to retrieve RAG context: {e}")
            # Return empty context rather than failing
            return {
                "agent": agent_id,
                "chunks_retrieved": 0,
                "chunks": [],
                "sources": [],
            }

    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract unique source documents from chunks.

        Args:
            chunks: Retrieved RAG chunks

        Returns:
            List of source documents
        """
        sources = {}

        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            doc_id = metadata.get("document_id")

            if doc_id and doc_id not in sources:
                sources[doc_id] = {
                    "document_id": doc_id,
                    "filename": metadata.get("filename", "Unknown"),
                    "page_number": metadata.get("page_number"),
                }

        return list(sources.values())

    def _format_user_message_with_context(
        self,
        user_message: str,
        rag_context: Dict[str, Any],
    ) -> str:
        """
        Format user message with RAG context for Claude.

        Args:
            user_message: Original user message
            rag_context: Retrieved RAG context

        Returns:
            Formatted message with context
        """
        if not rag_context["chunks"]:
            return user_message

        # Format context chunks
        context_text = rag_service.format_context_for_llm(
            chunks=rag_context["chunks"],
            max_chunks=5,
        )

        # Combine context with user message
        return f"""{context_text}

# User Question

{user_message}

Please answer based on the context provided above. Cite specific document sections and page numbers when referencing information."""

    async def generate_conversation_title(self, first_message: str) -> str:
        """
        Generate a concise title for a conversation from the first message.

        Args:
            first_message: First user message in conversation

        Returns:
            Generated title (max 50 chars)
        """
        try:
            response = await self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=50,
                temperature=0.5,
                system="Generate a very short title (max 6 words) for this conversation about building compliance. Be concise.",
                messages=[{
                    "role": "user",
                    "content": f"Generate a short title for this question: {first_message}"
                }],
            )

            title = response.content[0].text.strip()
            # Truncate to 50 chars if needed
            return title[:50] if len(title) > 50 else title

        except Exception as e:
            logger.error(f"Failed to generate title: {e}")
            # Fallback: use first 50 chars of message
            return first_message[:47] + "..." if len(first_message) > 50 else first_message


# Global chat service instance
chat_service = ChatService()

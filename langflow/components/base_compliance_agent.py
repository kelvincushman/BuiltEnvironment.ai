"""
Base Compliance Agent Component for Langflow

This is a custom Langflow component that provides base functionality
for all 13 specialist compliance agents.

Usage in Langflow:
1. Import this component
2. Drag onto canvas
3. Connect to Claude AI model
4. Configure agent_type parameter
"""

from langflow.custom import CustomComponent
from langflow.field_typing import Text
from typing import Dict, Any
import json


class BaseComplianceAgent(CustomComponent):
    display_name = "Base Compliance Agent"
    description = "Base component for UK Building Regulations compliance checking"
    documentation = "https://github.com/your-org/builtenvironment.ai"

    def build_config(self):
        return {
            "agent_type": {
                "display_name": "Agent Type",
                "info": "Type of compliance agent (fire_safety, structural, etc.)",
                "options": [
                    "fire_safety",
                    "structural",
                    "building_envelope",
                    "mechanical_services",
                    "electrical_services",
                    "accessibility",
                    "environmental_sustainability",
                    "health_safety",
                    "quality_assurance",
                    "legal_contracts",
                    "specialist_systems",
                    "external_works",
                    "finishes_interiors"
                ],
            },
            "document_text": {
                "display_name": "Document Text",
                "info": "Extracted text from building document",
                "multiline": True,
            },
            "document_metadata": {
                "display_name": "Document Metadata",
                "info": "JSON metadata about the document",
                "multiline": True,
            },
            "tenant_id": {
                "display_name": "Tenant ID",
                "info": "Tenant ID for multi-tenant isolation",
            },
        }

    def build(
        self,
        agent_type: str,
        document_text: str,
        document_metadata: str = "{}",
        tenant_id: str = "",
    ) -> Dict[str, Any]:
        """
        Build the base compliance agent.

        This component:
        1. Validates inputs
        2. Prepares document for analysis
        3. Returns structured data for downstream components
        """

        # Parse metadata
        try:
            metadata = json.loads(document_metadata)
        except:
            metadata = {}

        # Add tenant ID to metadata
        metadata["tenant_id"] = tenant_id
        metadata["agent_type"] = agent_type

        # Prepare output
        result = {
            "agent_type": agent_type,
            "document_text": document_text,
            "metadata": metadata,
            "text_length": len(document_text),
            "tenant_id": tenant_id,
            "status": "ready_for_analysis",
        }

        return result

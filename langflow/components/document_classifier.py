"""
Document Classifier Component for Langflow

This component analyzes a building document and classifies it by:
1. Document type (drawing, specification, calculation, report, etc.)
2. Building discipline (structural, fire safety, electrical, etc.)
3. Relevant UK Building Regulations parts
4. Which specialist agents should analyze it

Usage in Langflow:
1. Connect document input to this component
2. Component outputs routing information
3. Connect to appropriate specialist agent workflows
"""

from langflow.custom import CustomComponent
from langflow.field_typing import Text
from typing import Dict, Any, List
import json


class DocumentClassifier(CustomComponent):
    display_name = "Document Classifier"
    description = "Classifies building documents and routes to appropriate specialist agents"
    documentation = "https://github.com/your-org/builtenvironment.ai"

    def build_config(self):
        return {
            "document_text": {
                "display_name": "Document Text",
                "info": "Extracted text from the building document",
                "multiline": True,
            },
            "document_filename": {
                "display_name": "Document Filename",
                "info": "Original filename (helps with classification)",
            },
            "document_metadata": {
                "display_name": "Document Metadata",
                "info": "JSON metadata (file type, page count, etc.)",
                "multiline": True,
            },
            "tenant_id": {
                "display_name": "Tenant ID",
                "info": "Tenant ID for multi-tenant isolation",
            },
        }

    def build(
        self,
        document_text: str,
        document_filename: str = "",
        document_metadata: str = "{}",
        tenant_id: str = "",
    ) -> Dict[str, Any]:
        """
        Classify the document and determine routing.

        This component:
        1. Identifies document type
        2. Detects building disciplines
        3. Maps to UK Building Regulations parts
        4. Returns list of specialist agents to invoke
        """

        # Parse metadata
        try:
            metadata = json.loads(document_metadata)
        except:
            metadata = {}

        # Document type classification
        # In production, this would use Claude API for intelligent classification
        # For now, using keyword-based heuristics
        document_type = self._classify_document_type(document_text, document_filename)

        # Discipline detection
        disciplines = self._detect_disciplines(document_text, document_filename)

        # Regulation mapping
        regulations = self._map_regulations(disciplines, document_text)

        # Agent routing
        agents_to_invoke = self._determine_agents(disciplines, document_type)

        # Prepare classification result
        result = {
            "document_type": document_type,
            "disciplines": disciplines,
            "regulations": regulations,
            "agents_to_invoke": agents_to_invoke,
            "classification_confidence": self._calculate_confidence(document_text, disciplines),
            "tenant_id": tenant_id,
            "metadata": metadata,
            "routing_instructions": {
                "parallel_processing": len(agents_to_invoke) > 1,
                "priority_agents": self._prioritize_agents(agents_to_invoke, document_type),
            },
        }

        return result

    def _classify_document_type(self, text: str, filename: str) -> str:
        """
        Classify document type based on content and filename.

        Types: drawing, specification, calculation, report,
               fire_strategy, design_statement, schedule, certificate
        """
        text_lower = text.lower()
        filename_lower = filename.lower()

        # Drawing indicators
        if any(word in text_lower for word in ["scale 1:", "drawing no", "rev.", "north point"]):
            return "drawing"
        if any(ext in filename_lower for ext in [".dwg", ".dxf", ".pdf"] and "drg" in filename_lower):
            return "drawing"

        # Fire safety strategy
        if "fire safety strategy" in text_lower or "fire engineering" in text_lower:
            return "fire_strategy"

        # Calculation sheets
        if any(word in text_lower for word in ["calculation", "load case", "ultimate limit state"]):
            return "calculation"

        # Specification
        if "specification" in text_lower or "clause" in text_lower:
            return "specification"

        # Certificate
        if "certificate" in text_lower or "certified that" in text_lower:
            return "certificate"

        # Schedule (door schedule, window schedule, etc.)
        if "schedule" in text_lower and any(word in text_lower for word in ["door", "window", "finish"]):
            return "schedule"

        # Default to report
        return "report"

    def _detect_disciplines(self, text: str, filename: str) -> List[str]:
        """
        Detect which building disciplines are relevant.

        Returns list of disciplines from:
        structural, fire_safety, building_envelope, mechanical_services,
        electrical_services, accessibility, environmental_sustainability,
        health_safety, quality_assurance, legal_contracts,
        specialist_systems, external_works, finishes_interiors
        """
        disciplines = []
        text_lower = text.lower()

        # Structural engineering
        structural_keywords = ["structural", "foundation", "beam", "column", "slab", "eurocode", "steel frame", "concrete"]
        if any(kw in text_lower for kw in structural_keywords):
            disciplines.append("structural")

        # Fire safety
        fire_keywords = ["fire", "smoke", "sprinkler", "fire alarm", "fire rating", "means of escape", "compartmentation"]
        if any(kw in text_lower for kw in fire_keywords):
            disciplines.append("fire_safety")

        # Building envelope
        envelope_keywords = ["thermal", "insulation", "u-value", "glazing", "window", "external wall", "roof", "weatherproofing"]
        if any(kw in text_lower for kw in envelope_keywords):
            disciplines.append("building_envelope")

        # Mechanical services
        mechanical_keywords = ["hvac", "ventilation", "heating", "cooling", "plumbing", "drainage", "water supply", "air handling"]
        if any(kw in text_lower for kw in mechanical_keywords):
            disciplines.append("mechanical_services")

        # Electrical services
        electrical_keywords = ["electrical", "power", "lighting", "distribution board", "cable", "circuit", "bs 7671", "wiring"]
        if any(kw in text_lower for kw in electrical_keywords):
            disciplines.append("electrical_services")

        # Accessibility
        accessibility_keywords = ["accessibility", "disabled access", "part m", "wheelchair", "accessible", "inclusive design"]
        if any(kw in text_lower for kw in accessibility_keywords):
            disciplines.append("accessibility")

        # Environmental sustainability
        environmental_keywords = ["energy efficiency", "breeam", "leed", "sustainability", "carbon", "renewable", "solar", "environmental"]
        if any(kw in text_lower for kw in environmental_keywords):
            disciplines.append("environmental_sustainability")

        # Health & safety
        hs_keywords = ["health and safety", "cdm", "construction phase plan", "risk assessment", "method statement"]
        if any(kw in text_lower for kw in hs_keywords):
            disciplines.append("health_safety")

        # Quality assurance
        qa_keywords = ["testing", "commissioning", "inspection", "certificate", "test report", "compliance certificate"]
        if any(kw in text_lower for kw in qa_keywords):
            disciplines.append("quality_assurance")

        # Legal & contracts
        legal_keywords = ["contract", "jct", "nec", "warranty", "guarantee", "agreement", "tender"]
        if any(kw in text_lower for kw in legal_keywords):
            disciplines.append("legal_contracts")

        # Specialist systems
        specialist_keywords = ["lift", "elevator", "escalator", "bms", "building management", "access control", "cctv"]
        if any(kw in text_lower for kw in specialist_keywords):
            disciplines.append("specialist_systems")

        # External works
        external_keywords = ["drainage", "landscaping", "paving", "roads", "highways", "suds", "attenuation"]
        if any(kw in text_lower for kw in external_keywords):
            disciplines.append("external_works")

        # Finishes & interiors
        finishes_keywords = ["finishes", "flooring", "ceiling", "partition", "acoustic", "interior", "joinery"]
        if any(kw in text_lower for kw in finishes_keywords):
            disciplines.append("finishes_interiors")

        # If no disciplines detected, flag for manual review
        if not disciplines:
            disciplines.append("requires_manual_classification")

        return disciplines

    def _map_regulations(self, disciplines: List[str], text: str) -> List[str]:
        """
        Map disciplines to UK Building Regulations parts.
        """
        regulations = set()
        text_lower = text.lower()

        # Discipline to regulation mapping
        discipline_regulation_map = {
            "structural": ["Part A - Structure"],
            "fire_safety": ["Part B - Fire Safety"],
            "building_envelope": ["Part C - Site Preparation", "Part L - Conservation of Fuel and Power"],
            "mechanical_services": ["Part F - Ventilation", "Part G - Sanitation", "Part H - Drainage", "Part J - Combustion"],
            "electrical_services": ["Part P - Electrical Safety"],
            "accessibility": ["Part M - Access"],
            "environmental_sustainability": ["Part L - Conservation of Fuel and Power"],
            "health_safety": ["CDM Regulations 2015"],
            "finishes_interiors": ["Part E - Resistance to Sound", "Part B - Fire Safety (Linings)"],
        }

        for discipline in disciplines:
            if discipline in discipline_regulation_map:
                regulations.update(discipline_regulation_map[discipline])

        # Also detect explicit mentions of regulations in text
        regulation_patterns = {
            "part a": "Part A - Structure",
            "part b": "Part B - Fire Safety",
            "part c": "Part C - Site Preparation",
            "part e": "Part E - Resistance to Sound",
            "part f": "Part F - Ventilation",
            "part g": "Part G - Sanitation",
            "part h": "Part H - Drainage",
            "part j": "Part J - Combustion",
            "part l": "Part L - Conservation of Fuel and Power",
            "part m": "Part M - Access",
            "part p": "Part P - Electrical Safety",
        }

        for pattern, regulation in regulation_patterns.items():
            if pattern in text_lower:
                regulations.add(regulation)

        return sorted(list(regulations))

    def _determine_agents(self, disciplines: List[str], document_type: str) -> List[str]:
        """
        Determine which specialist agents should analyze this document.
        """
        # Direct mapping from disciplines to agent IDs
        return disciplines

    def _prioritize_agents(self, agents: List[str], document_type: str) -> List[str]:
        """
        Prioritize agents based on document type.
        For fire strategies, fire_safety is highest priority.
        For structural calculations, structural is highest priority.
        """
        priority_map = {
            "fire_strategy": ["fire_safety"],
            "calculation": ["structural"],
            "drawing": [],  # No specific priority
        }

        priority_agents = priority_map.get(document_type, [])

        # Return prioritized list: priority agents first, then others
        other_agents = [a for a in agents if a not in priority_agents]
        return priority_agents + other_agents

    def _calculate_confidence(self, text: str, disciplines: List[str]) -> float:
        """
        Calculate confidence score for the classification.
        Based on text length, keyword matches, etc.
        """
        if not text or len(text) < 100:
            return 0.3  # Low confidence for short documents

        if "requires_manual_classification" in disciplines:
            return 0.4  # Low confidence if no disciplines detected

        # Higher confidence if multiple strong indicators
        if len(disciplines) >= 2:
            return 0.85

        if len(disciplines) == 1:
            return 0.75

        return 0.6

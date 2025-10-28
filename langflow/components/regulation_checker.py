"""
Regulation Checker Component for Langflow

This component checks specific UK Building Regulations requirements against
document content. It validates compliance with:
- Building Regulations Parts A-P
- British Standards (BS)
- Eurocodes
- Other relevant standards

Usage in Langflow:
1. Connect to document text and regulation requirements
2. Component checks each requirement
3. Outputs compliance findings with evidence
"""

from langflow.custom import CustomComponent
from langflow.field_typing import Text
from typing import Dict, Any, List
import json
import re


class RegulationChecker(CustomComponent):
    display_name = "Regulation Checker"
    description = "Checks UK Building Regulations compliance requirements"
    documentation = "https://github.com/your-org/builtenvironment.ai"

    def build_config(self):
        return {
            "document_text": {
                "display_name": "Document Text",
                "info": "Full text of the building document",
                "multiline": True,
            },
            "regulation_requirements": {
                "display_name": "Regulation Requirements",
                "info": "JSON array of regulation requirements to check",
                "multiline": True,
            },
            "agent_type": {
                "display_name": "Agent Type",
                "info": "Type of specialist agent (fire_safety, structural, etc.)",
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
                    "finishes_interiors",
                ],
            },
        }

    def build(
        self,
        document_text: str,
        regulation_requirements: str,
        agent_type: str = "fire_safety",
    ) -> Dict[str, Any]:
        """
        Check regulation compliance requirements.

        This component:
        1. Parses regulation requirements for the agent type
        2. Searches document for compliance evidence
        3. Validates each requirement
        4. Returns findings with compliance status
        """

        # Parse requirements
        try:
            requirements_list = json.loads(regulation_requirements) if isinstance(regulation_requirements, str) else regulation_requirements
        except:
            requirements_list = []

        if not isinstance(requirements_list, list):
            requirements_list = [requirements_list]

        # Filter requirements for this agent type
        relevant_requirements = [
            req for req in requirements_list
            if req.get("agent_type", agent_type) == agent_type
        ]

        # Check each requirement
        compliance_findings = []
        for requirement in relevant_requirements:
            finding = self._check_requirement(requirement, document_text, agent_type)
            compliance_findings.append(finding)

        # Generate compliance summary
        summary = self._generate_compliance_summary(compliance_findings, agent_type)

        result = {
            "compliance_findings": compliance_findings,
            "summary": summary,
            "agent_type": agent_type,
            "total_requirements_checked": len(compliance_findings),
            "requirements_met": sum(1 for f in compliance_findings if f["is_compliant"]),
            "requirements_not_met": sum(1 for f in compliance_findings if not f["is_compliant"]),
        }

        return result

    def _check_requirement(
        self, requirement: Dict[str, Any], document_text: str, agent_type: str
    ) -> Dict[str, Any]:
        """
        Check a single regulation requirement.
        """
        regulation = requirement.get("regulation", "")
        requirement_text = requirement.get("requirement", "")
        keywords = requirement.get("keywords", [])
        required_values = requirement.get("required_values", {})

        # Search for regulation mention
        regulation_mentioned = self._check_regulation_mentioned(document_text, regulation)

        # Search for requirement keywords
        keywords_found = self._check_keywords(document_text, keywords)

        # Validate required values (if specified)
        values_compliant = self._check_required_values(
            document_text, required_values
        ) if required_values else True

        # Calculate compliance status
        is_compliant = regulation_mentioned and (
            len(keywords_found) >= len(keywords) * 0.5  # At least 50% keywords found
        ) and values_compliant

        # Calculate confidence
        confidence = self._calculate_requirement_confidence(
            regulation_mentioned,
            keywords_found,
            keywords,
            values_compliant,
        )

        # Create finding
        finding = {
            "id": requirement.get("id", f"{regulation}_{hash(requirement_text)}"),
            "regulation": regulation,
            "requirement": requirement_text,
            "is_compliant": is_compliant,
            "confidence": confidence,
            "regulation_mentioned": regulation_mentioned,
            "keywords_found": keywords_found,
            "total_keywords": len(keywords),
            "values_compliant": values_compliant,
            "agent_type": agent_type,
            "description": self._generate_finding_description(
                regulation, requirement_text, is_compliant, confidence
            ),
        }

        return finding

    def _check_regulation_mentioned(self, text: str, regulation: str) -> bool:
        """
        Check if regulation is explicitly mentioned in document.
        """
        if not regulation:
            return False

        # Search for regulation (case insensitive)
        pattern = re.escape(regulation)
        match = re.search(pattern, text, re.IGNORECASE)

        return match is not None

    def _check_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """
        Check which keywords are present in the document.
        Returns list of found keywords.
        """
        found = []
        text_lower = text.lower()

        for keyword in keywords:
            if keyword.lower() in text_lower:
                found.append(keyword)

        return found

    def _check_required_values(
        self, text: str, required_values: Dict[str, Any]
    ) -> bool:
        """
        Check if required values are present and meet thresholds.

        Example required_values:
        {
            "fire_rating_minutes": {"min": 60},
            "u_value": {"max": 0.28},
            "thickness_mm": {"min": 100}
        }
        """
        for value_name, constraints in required_values.items():
            # Build search pattern based on value name
            value_pattern = self._build_value_pattern(value_name)

            # Find values in text
            matches = re.finditer(value_pattern, text, re.IGNORECASE)

            found_compliant_value = False
            for match in matches:
                try:
                    value = float(match.group(1))

                    # Check constraints
                    if "min" in constraints and value < constraints["min"]:
                        continue
                    if "max" in constraints and value > constraints["max"]:
                        continue
                    if "exact" in constraints and value != constraints["exact"]:
                        continue

                    # If we get here, value meets constraints
                    found_compliant_value = True
                    break
                except (ValueError, IndexError):
                    continue

            if not found_compliant_value:
                return False

        return True

    def _build_value_pattern(self, value_name: str) -> str:
        """
        Build regex pattern for extracting values.
        """
        patterns = {
            "fire_rating_minutes": r"(\d+)\s*(?:minute|min)\s*fire\s*(?:rating|resistance)",
            "u_value": r"U[-\s]?value[s]?[\s:=]+(\d+\.?\d*)",
            "thickness_mm": r"(\d+)\s*mm\s*thick",
            "load_capacity_kn": r"(\d+\.?\d*)\s*kN",
            "height_m": r"(\d+\.?\d*)\s*(?:m|metre|meter)",
        }

        return patterns.get(value_name, r"(\d+\.?\d*)")

    def _calculate_requirement_confidence(
        self,
        regulation_mentioned: bool,
        keywords_found: List[str],
        total_keywords: List[str],
        values_compliant: bool,
    ) -> float:
        """
        Calculate confidence score for requirement check.
        """
        confidence = 0.0

        # Regulation mentioned: +0.3
        if regulation_mentioned:
            confidence += 0.3

        # Keyword match rate: up to +0.5
        if total_keywords:
            keyword_rate = len(keywords_found) / len(total_keywords)
            confidence += 0.5 * keyword_rate

        # Values compliant: +0.2
        if values_compliant:
            confidence += 0.2

        return min(1.0, confidence)

    def _generate_finding_description(
        self, regulation: str, requirement: str, is_compliant: bool, confidence: float
    ) -> str:
        """
        Generate human-readable finding description.
        """
        status = "compliant" if is_compliant else "non-compliant"
        confidence_pct = int(confidence * 100)

        return f"{regulation}: {requirement} - {status} ({confidence_pct}% confidence)"

    def _generate_compliance_summary(
        self, findings: List[Dict[str, Any]], agent_type: str
    ) -> Dict[str, Any]:
        """
        Generate summary of compliance findings.
        """
        if not findings:
            return {
                "agent_type": agent_type,
                "total_requirements": 0,
                "compliant_count": 0,
                "non_compliant_count": 0,
                "compliance_rate": 0,
                "average_confidence": 0,
                "regulations_checked": [],
            }

        compliant_count = sum(1 for f in findings if f["is_compliant"])
        non_compliant_count = len(findings) - compliant_count
        compliance_rate = (compliant_count / len(findings) * 100) if findings else 0

        average_confidence = (
            sum(f["confidence"] for f in findings) / len(findings)
            if findings
            else 0
        )

        regulations_checked = list(set(f["regulation"] for f in findings))

        return {
            "agent_type": agent_type,
            "total_requirements": len(findings),
            "compliant_count": compliant_count,
            "non_compliant_count": non_compliant_count,
            "compliance_rate": round(compliance_rate, 2),
            "average_confidence": round(average_confidence, 2),
            "regulations_checked": regulations_checked,
        }

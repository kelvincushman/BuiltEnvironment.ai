"""
Evidence Extractor Component for Langflow

This component extracts specific evidence from building documents to support
compliance findings. It identifies:
1. Direct quotes from the document
2. Specific regulation references
3. Technical specifications
4. Calculations and values
5. Drawing references

Usage in Langflow:
1. Connect to document text and compliance findings
2. Component extracts supporting evidence for each finding
3. Outputs structured evidence with page numbers and context
"""

from langflow.custom import CustomComponent
from langflow.field_typing import Text
from typing import Dict, Any, List
import json
import re


class EvidenceExtractor(CustomComponent):
    display_name = "Evidence Extractor"
    description = "Extracts supporting evidence and quotes from building documents"
    documentation = "https://github.com/your-org/builtenvironment.ai"

    def build_config(self):
        return {
            "document_text": {
                "display_name": "Document Text",
                "info": "Full text of the building document",
                "multiline": True,
            },
            "compliance_findings": {
                "display_name": "Compliance Findings",
                "info": "JSON array of compliance findings to extract evidence for",
                "multiline": True,
            },
            "context_window": {
                "display_name": "Context Window (characters)",
                "info": "How many characters before/after the quote to include as context",
                "value": 200,
            },
            "max_quotes_per_finding": {
                "display_name": "Max Quotes Per Finding",
                "info": "Maximum number of supporting quotes to extract per finding",
                "value": 3,
            },
        }

    def build(
        self,
        document_text: str,
        compliance_findings: str,
        context_window: int = 200,
        max_quotes_per_finding: int = 3,
    ) -> Dict[str, Any]:
        """
        Extract supporting evidence from document for each compliance finding.

        This component:
        1. Parses compliance findings
        2. Searches document for relevant evidence
        3. Extracts quotes with context
        4. Identifies page numbers and sections
        5. Returns structured evidence for each finding
        """

        # Parse findings
        try:
            findings_list = json.loads(compliance_findings) if isinstance(compliance_findings, str) else compliance_findings
        except:
            findings_list = []

        if not isinstance(findings_list, list):
            findings_list = [findings_list]

        # Extract evidence for each finding
        findings_with_evidence = []
        for finding in findings_list:
            evidence = self._extract_evidence_for_finding(
                finding, document_text, context_window, max_quotes_per_finding
            )
            finding_with_evidence = {
                **finding,
                "evidence": evidence,
                "evidence_count": len(evidence),
            }
            findings_with_evidence.append(finding_with_evidence)

        # Generate evidence summary
        summary = self._generate_evidence_summary(findings_with_evidence)

        result = {
            "findings_with_evidence": findings_with_evidence,
            "summary": summary,
            "total_findings": len(findings_with_evidence),
            "total_evidence_items": sum(f["evidence_count"] for f in findings_with_evidence),
        }

        return result

    def _extract_evidence_for_finding(
        self,
        finding: Dict[str, Any],
        document_text: str,
        context_window: int,
        max_quotes: int,
    ) -> List[Dict[str, Any]]:
        """
        Extract evidence for a single compliance finding.
        """
        evidence_items = []

        # Get search terms from finding
        regulation = finding.get("regulation", "")
        description = finding.get("description", "")
        keywords = finding.get("keywords", [])

        # Extract keywords from description if not provided
        if not keywords:
            keywords = self._extract_keywords(description)

        # Search for regulation references
        regulation_evidence = self._find_regulation_references(
            document_text, regulation, context_window
        )
        evidence_items.extend(regulation_evidence)

        # Search for keyword matches
        keyword_evidence = self._find_keyword_matches(
            document_text, keywords, context_window, max_quotes - len(evidence_items)
        )
        evidence_items.extend(keyword_evidence)

        # Search for technical specifications
        spec_evidence = self._find_technical_specifications(
            document_text, finding, context_window
        )
        evidence_items.extend(spec_evidence)

        # Search for calculations and values
        if finding.get("requires_calculation", False):
            calc_evidence = self._find_calculations(document_text, context_window)
            evidence_items.extend(calc_evidence)

        # Limit to max quotes
        evidence_items = evidence_items[:max_quotes]

        # Add metadata
        for item in evidence_items:
            item["finding_id"] = finding.get("id", "")
            item["regulation"] = regulation

        return evidence_items

    def _find_regulation_references(
        self, text: str, regulation: str, context_window: int
    ) -> List[Dict[str, Any]]:
        """
        Find direct references to the regulation in the document.
        """
        evidence = []

        if not regulation:
            return evidence

        # Search for regulation mentions
        # e.g., "Part B", "Part A", "BS 7671", "Eurocode 2"
        pattern = re.escape(regulation)
        matches = re.finditer(pattern, text, re.IGNORECASE)

        for match in matches:
            start = max(0, match.start() - context_window)
            end = min(len(text), match.end() + context_window)

            quote = text[start:end].strip()
            page_number = self._estimate_page_number(text, match.start())

            evidence.append({
                "type": "regulation_reference",
                "quote": quote,
                "highlighted_text": regulation,
                "page_number": page_number,
                "character_position": match.start(),
                "confidence": 0.95,  # High confidence for direct regulation reference
            })

            # Limit to 2 regulation references
            if len(evidence) >= 2:
                break

        return evidence

    def _find_keyword_matches(
        self, text: str, keywords: List[str], context_window: int, max_matches: int
    ) -> List[Dict[str, Any]]:
        """
        Find keyword matches in the document.
        """
        evidence = []

        for keyword in keywords:
            if len(evidence) >= max_matches:
                break

            # Search for keyword (case insensitive)
            pattern = re.escape(keyword)
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                if len(evidence) >= max_matches:
                    break

                start = max(0, match.start() - context_window)
                end = min(len(text), match.end() + context_window)

                quote = text[start:end].strip()
                page_number = self._estimate_page_number(text, match.start())

                evidence.append({
                    "type": "keyword_match",
                    "quote": quote,
                    "highlighted_text": keyword,
                    "page_number": page_number,
                    "character_position": match.start(),
                    "confidence": 0.75,
                })

        return evidence

    def _find_technical_specifications(
        self, text: str, finding: Dict[str, Any], context_window: int
    ) -> List[Dict[str, Any]]:
        """
        Find technical specifications like U-values, load ratings, fire ratings, etc.
        """
        evidence = []

        # Common specification patterns
        patterns = {
            "u_value": r"U[-\s]?value[s]?[\s:=]+(\d+\.?\d*)\s*W/m²K",
            "fire_rating": r"(\d+)\s*(?:minute|min|hour|hr)\s*fire\s*resistance",
            "load_capacity": r"(\d+\.?\d*)\s*kN/m²",
            "thermal_resistance": r"R[-\s]?value[s]?[\s:=]+(\d+\.?\d*)",
            "thickness": r"(\d+)\s*mm\s*thick",
        }

        for spec_type, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                if len(evidence) >= 2:  # Limit technical specs
                    break

                start = max(0, match.start() - context_window)
                end = min(len(text), match.end() + context_window)

                quote = text[start:end].strip()
                page_number = self._estimate_page_number(text, match.start())

                evidence.append({
                    "type": "technical_specification",
                    "spec_type": spec_type,
                    "quote": quote,
                    "highlighted_text": match.group(0),
                    "value": match.group(1) if match.groups() else None,
                    "page_number": page_number,
                    "character_position": match.start(),
                    "confidence": 0.90,
                })

        return evidence

    def _find_calculations(
        self, text: str, context_window: int
    ) -> List[Dict[str, Any]]:
        """
        Find calculations and formulas in the document.
        """
        evidence = []

        # Look for calculation patterns
        # e.g., "= 150 kN", "Total load = 45 kN/m²"
        calc_pattern = r"([A-Za-z\s]+)\s*=\s*(\d+\.?\d*)\s*([A-Za-z/²³]+)"
        matches = re.finditer(calc_pattern, text)

        for match in matches:
            if len(evidence) >= 2:
                break

            start = max(0, match.start() - context_window)
            end = min(len(text), match.end() + context_window)

            quote = text[start:end].strip()
            page_number = self._estimate_page_number(text, match.start())

            evidence.append({
                "type": "calculation",
                "quote": quote,
                "highlighted_text": match.group(0),
                "page_number": page_number,
                "character_position": match.start(),
                "confidence": 0.80,
            })

        return evidence

    def _extract_keywords(self, description: str) -> List[str]:
        """
        Extract important keywords from finding description.
        """
        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "should", "could", "may", "might", "must", "can", "this",
            "that", "these", "those", "it", "its", "they", "their", "them"
        }

        # Extract words
        words = re.findall(r'\b[A-Za-z]{4,}\b', description.lower())

        # Filter stop words and return unique keywords
        keywords = [w for w in words if w not in stop_words]
        return list(set(keywords))[:5]  # Top 5 unique keywords

    def _estimate_page_number(self, text: str, position: int) -> int:
        """
        Estimate page number based on character position.
        Assumes ~3000 characters per page.
        """
        return (position // 3000) + 1

    def _generate_evidence_summary(
        self, findings_with_evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics for extracted evidence.
        """
        total_evidence = sum(f["evidence_count"] for f in findings_with_evidence)

        evidence_by_type = {}
        for finding in findings_with_evidence:
            for evidence_item in finding.get("evidence", []):
                evidence_type = evidence_item.get("type", "unknown")
                evidence_by_type[evidence_type] = evidence_by_type.get(evidence_type, 0) + 1

        findings_without_evidence = sum(
            1 for f in findings_with_evidence if f["evidence_count"] == 0
        )

        average_evidence_per_finding = (
            total_evidence / len(findings_with_evidence)
            if findings_with_evidence
            else 0
        )

        return {
            "total_evidence_items": total_evidence,
            "evidence_by_type": evidence_by_type,
            "findings_without_evidence": findings_without_evidence,
            "average_evidence_per_finding": round(average_evidence_per_finding, 2),
        }

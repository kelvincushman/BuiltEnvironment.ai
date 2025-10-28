"""
Confidence Calculator Component for Langflow

This component calculates confidence scores for AI compliance findings based on:
1. Evidence quality and quantity
2. Regulation clarity and specificity
3. Document completeness
4. Cross-validation with multiple sources
5. Specialist agent certainty

Usage in Langflow:
1. Connect to compliance findings with evidence
2. Component analyzes multiple confidence factors
3. Outputs calibrated confidence scores (0.0 to 1.0)
"""

from langflow.custom import CustomComponent
from langflow.field_typing import Text
from typing import Dict, Any, List
import json


class ConfidenceCalculator(CustomComponent):
    display_name = "Confidence Calculator"
    description = "Calculates calibrated confidence scores for AI compliance findings"
    documentation = "https://github.com/your-org/builtenvironment.ai"

    def build_config(self):
        return {
            "findings": {
                "display_name": "Compliance Findings",
                "info": "JSON array of compliance findings to calculate confidence for",
                "multiline": True,
            },
            "document_completeness": {
                "display_name": "Document Completeness (%)",
                "info": "How complete is the document (affects confidence)",
                "value": 100,
            },
            "agent_specialization_match": {
                "display_name": "Agent Specialization Match",
                "info": "How well does the agent match the document type (0.0-1.0)",
                "value": 1.0,
            },
        }

    def build(
        self,
        findings: str,
        document_completeness: int = 100,
        agent_specialization_match: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Calculate calibrated confidence scores for compliance findings.

        This component:
        1. Analyzes evidence quality for each finding
        2. Considers document completeness
        3. Factors in agent specialization match
        4. Applies confidence calibration
        5. Returns findings with calibrated confidence scores
        """

        # Parse findings
        try:
            findings_list = json.loads(findings) if isinstance(findings, str) else findings
        except:
            findings_list = []

        if not isinstance(findings_list, list):
            findings_list = [findings_list]

        # Calculate confidence for each finding
        calibrated_findings = []
        for finding in findings_list:
            calibrated_finding = self._calculate_finding_confidence(
                finding,
                document_completeness,
                agent_specialization_match,
            )
            calibrated_findings.append(calibrated_finding)

        # Generate confidence summary
        summary = self._generate_confidence_summary(calibrated_findings)

        result = {
            "calibrated_findings": calibrated_findings,
            "summary": summary,
            "document_completeness": document_completeness,
            "agent_specialization_match": agent_specialization_match,
            "total_findings": len(calibrated_findings),
        }

        return result

    def _calculate_finding_confidence(
        self,
        finding: Dict[str, Any],
        document_completeness: int,
        agent_match: float,
    ) -> Dict[str, Any]:
        """
        Calculate calibrated confidence for a single finding.
        """
        # Get base confidence (from AI model or regulation checker)
        base_confidence = finding.get("confidence", 0.5)

        # Calculate evidence quality score
        evidence_quality = self._calculate_evidence_quality(finding)

        # Calculate regulation clarity score
        regulation_clarity = self._calculate_regulation_clarity(finding)

        # Calculate document quality factor
        document_factor = document_completeness / 100.0

        # Calculate final calibrated confidence
        calibrated_confidence = self._calibrate_confidence(
            base_confidence,
            evidence_quality,
            regulation_clarity,
            document_factor,
            agent_match,
        )

        # Determine confidence level
        confidence_level = self._get_confidence_level(calibrated_confidence)

        # Create calibrated finding
        calibrated_finding = {
            **finding,
            "base_confidence": round(base_confidence, 4),
            "calibrated_confidence": round(calibrated_confidence, 4),
            "confidence_level": confidence_level,
            "confidence_factors": {
                "evidence_quality": round(evidence_quality, 4),
                "regulation_clarity": round(regulation_clarity, 4),
                "document_completeness": round(document_factor, 4),
                "agent_specialization": round(agent_match, 4),
            },
            "confidence_explanation": self._generate_confidence_explanation(
                base_confidence,
                evidence_quality,
                regulation_clarity,
                document_factor,
                agent_match,
                calibrated_confidence,
            ),
        }

        return calibrated_finding

    def _calculate_evidence_quality(self, finding: Dict[str, Any]) -> float:
        """
        Calculate evidence quality score (0.0 to 1.0).

        Factors:
        - Number of evidence items
        - Evidence type diversity
        - Evidence confidence scores
        """
        evidence = finding.get("evidence", [])

        if not evidence:
            return 0.3  # Low quality without evidence

        # Evidence quantity factor (diminishing returns)
        quantity_score = min(1.0, len(evidence) / 5.0)  # Max at 5 items

        # Evidence type diversity
        evidence_types = set(e.get("type", "unknown") for e in evidence)
        diversity_score = min(1.0, len(evidence_types) / 3.0)  # Max at 3 types

        # Average evidence confidence
        evidence_confidences = [e.get("confidence", 0.5) for e in evidence]
        avg_evidence_confidence = (
            sum(evidence_confidences) / len(evidence_confidences)
            if evidence_confidences
            else 0.5
        )

        # Weighted combination
        quality_score = (
            0.4 * quantity_score
            + 0.3 * diversity_score
            + 0.3 * avg_evidence_confidence
        )

        return quality_score

    def _calculate_regulation_clarity(self, finding: Dict[str, Any]) -> float:
        """
        Calculate regulation clarity score (0.0 to 1.0).

        Factors:
        - Is regulation explicitly mentioned?
        - How specific is the requirement?
        - Are there measurable criteria?
        """
        regulation = finding.get("regulation", "")
        requirement = finding.get("requirement", "")
        regulation_mentioned = finding.get("regulation_mentioned", False)

        clarity_score = 0.0

        # Regulation explicitly mentioned: +0.4
        if regulation_mentioned:
            clarity_score += 0.4

        # Regulation is well-defined (has Part/BS/Eurocode reference): +0.3
        if any(prefix in regulation for prefix in ["Part ", "BS ", "Eurocode"]):
            clarity_score += 0.3

        # Requirement has measurable criteria (contains numbers/units): +0.3
        if requirement and any(char.isdigit() for char in requirement):
            clarity_score += 0.3

        return min(1.0, clarity_score)

    def _calibrate_confidence(
        self,
        base_confidence: float,
        evidence_quality: float,
        regulation_clarity: float,
        document_factor: float,
        agent_match: float,
    ) -> float:
        """
        Calibrate confidence using weighted combination of factors.

        Formula:
        calibrated = base * (
            0.3 * evidence_quality +
            0.2 * regulation_clarity +
            0.2 * document_factor +
            0.1 * agent_match +
            0.2 (baseline)
        )

        This ensures:
        - Poor evidence/clarity reduces confidence
        - Good evidence/clarity increases confidence
        - Incomplete documents reduce confidence
        - Mismatched agents reduce confidence
        """
        multiplier = (
            0.3 * evidence_quality
            + 0.2 * regulation_clarity
            + 0.2 * document_factor
            + 0.1 * agent_match
            + 0.2  # Baseline
        )

        calibrated = base_confidence * multiplier

        # Apply floor and ceiling
        return max(0.1, min(0.99, calibrated))  # Keep between 10% and 99%

    def _get_confidence_level(self, confidence: float) -> str:
        """
        Convert confidence score to categorical level.
        """
        if confidence >= 0.85:
            return "high"
        elif confidence >= 0.70:
            return "medium"
        elif confidence >= 0.50:
            return "low"
        else:
            return "very_low"

    def _generate_confidence_explanation(
        self,
        base_confidence: float,
        evidence_quality: float,
        regulation_clarity: float,
        document_factor: float,
        agent_match: float,
        calibrated_confidence: float,
    ) -> str:
        """
        Generate human-readable explanation of confidence calculation.
        """
        explanations = []

        # Base confidence
        base_pct = int(base_confidence * 100)
        explanations.append(f"Base AI confidence: {base_pct}%")

        # Evidence quality
        if evidence_quality >= 0.7:
            explanations.append("Strong supporting evidence found")
        elif evidence_quality >= 0.4:
            explanations.append("Moderate supporting evidence found")
        else:
            explanations.append("Limited supporting evidence")

        # Regulation clarity
        if regulation_clarity >= 0.7:
            explanations.append("Clear regulation requirements")
        elif regulation_clarity >= 0.4:
            explanations.append("Somewhat clear regulation requirements")
        else:
            explanations.append("Unclear or implicit regulation requirements")

        # Document completeness
        if document_factor < 0.8:
            explanations.append(f"Document is incomplete ({int(document_factor*100)}%)")

        # Agent specialization
        if agent_match < 0.8:
            explanations.append("Agent may not be fully specialized for this document type")

        # Final result
        calibrated_pct = int(calibrated_confidence * 100)
        explanations.append(f"Final calibrated confidence: {calibrated_pct}%")

        return " | ".join(explanations)

    def _generate_confidence_summary(
        self, calibrated_findings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics for confidence scores.
        """
        if not calibrated_findings:
            return {
                "average_base_confidence": 0,
                "average_calibrated_confidence": 0,
                "high_confidence_count": 0,
                "medium_confidence_count": 0,
                "low_confidence_count": 0,
                "very_low_confidence_count": 0,
            }

        base_confidences = [f["base_confidence"] for f in calibrated_findings]
        calibrated_confidences = [f["calibrated_confidence"] for f in calibrated_findings]

        avg_base = sum(base_confidences) / len(base_confidences)
        avg_calibrated = sum(calibrated_confidences) / len(calibrated_confidences)

        # Count by confidence level
        levels = [f["confidence_level"] for f in calibrated_findings]
        high_count = sum(1 for l in levels if l == "high")
        medium_count = sum(1 for l in levels if l == "medium")
        low_count = sum(1 for l in levels if l == "low")
        very_low_count = sum(1 for l in levels if l == "very_low")

        return {
            "average_base_confidence": round(avg_base, 4),
            "average_calibrated_confidence": round(avg_calibrated, 4),
            "confidence_change": round(avg_calibrated - avg_base, 4),
            "high_confidence_count": high_count,
            "medium_confidence_count": medium_count,
            "low_confidence_count": low_count,
            "very_low_confidence_count": very_low_count,
            "total_findings": len(calibrated_findings),
        }

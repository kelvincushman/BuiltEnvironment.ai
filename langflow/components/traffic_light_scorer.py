"""
Traffic Light Scorer Component for Langflow

This component applies the Green/Amber/Red traffic light scoring system
to compliance findings from specialist agents.

Scoring System:
- 🟢 GREEN: Compliant (confidence >= 85%)
- 🟡 AMBER: Requires Review (70% <= confidence < 85%)
- 🔴 RED: Non-Compliant (confidence < 70%)

Usage in Langflow:
1. Receives compliance findings from specialist agents
2. Applies traffic light scoring based on confidence and compliance status
3. Outputs color-coded results for WYSIWYG editor display
"""

from langflow.custom import CustomComponent
from langflow.field_typing import Text
from typing import Dict, Any, List
import json
from enum import Enum


class ComplianceStatus(str, Enum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"


class TrafficLightScorer(CustomComponent):
    display_name = "Traffic Light Scorer"
    description = "Applies Green/Amber/Red scoring to compliance findings"
    documentation = "https://github.com/your-org/builtenvironment.ai"

    def build_config(self):
        return {
            "findings": {
                "display_name": "Compliance Findings",
                "info": "JSON array of compliance findings from specialist agents",
                "multiline": True,
            },
            "green_threshold": {
                "display_name": "Green Threshold (%)",
                "info": "Minimum confidence for green status (default: 85%)",
                "value": 85,
            },
            "amber_threshold": {
                "display_name": "Amber Threshold (%)",
                "info": "Minimum confidence for amber status (default: 70%)",
                "value": 70,
            },
            "strict_mode": {
                "display_name": "Strict Mode",
                "info": "If true, any non-compliance is automatically red regardless of confidence",
                "value": False,
            },
        }

    def build(
        self,
        findings: str,
        green_threshold: int = 85,
        amber_threshold: int = 70,
        strict_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Apply traffic light scoring to compliance findings.

        This component:
        1. Parses compliance findings from specialist agents
        2. Calculates traffic light status for each finding
        3. Computes overall document status
        4. Returns color-coded results with statistics
        """

        # Parse findings
        try:
            findings_list = json.loads(findings) if isinstance(findings, str) else findings
        except:
            findings_list = []

        if not isinstance(findings_list, list):
            findings_list = [findings_list]

        # Score each finding
        scored_findings = []
        for finding in findings_list:
            scored_finding = self._score_finding(
                finding, green_threshold, amber_threshold, strict_mode
            )
            scored_findings.append(scored_finding)

        # Calculate overall status
        overall_status = self._calculate_overall_status(scored_findings)

        # Generate statistics
        statistics = self._generate_statistics(scored_findings)

        # Prepare result
        result = {
            "scored_findings": scored_findings,
            "overall_status": overall_status,
            "statistics": statistics,
            "thresholds": {
                "green": green_threshold,
                "amber": amber_threshold,
            },
            "strict_mode": strict_mode,
            "total_findings": len(scored_findings),
        }

        return result

    def _score_finding(
        self,
        finding: Dict[str, Any],
        green_threshold: int,
        amber_threshold: int,
        strict_mode: bool,
    ) -> Dict[str, Any]:
        """
        Score a single compliance finding with traffic light status.
        """
        # Extract confidence and compliance status
        confidence = finding.get("confidence", 0) * 100  # Convert to percentage
        is_compliant = finding.get("is_compliant", True)
        regulation = finding.get("regulation", "Unknown")
        description = finding.get("description", "")
        evidence = finding.get("evidence", "")

        # Determine traffic light status
        if strict_mode and not is_compliant:
            # In strict mode, any non-compliance is red
            status = ComplianceStatus.RED
        elif not is_compliant:
            # Non-compliant findings are at least amber, possibly red
            if confidence >= green_threshold:
                # High confidence non-compliance = red
                status = ComplianceStatus.RED
            elif confidence >= amber_threshold:
                # Medium confidence non-compliance = red
                status = ComplianceStatus.RED
            else:
                # Low confidence non-compliance = red (but flagged for review)
                status = ComplianceStatus.RED
        else:
            # Compliant findings - score by confidence
            if confidence >= green_threshold:
                status = ComplianceStatus.GREEN
            elif confidence >= amber_threshold:
                status = ComplianceStatus.AMBER
            else:
                # Low confidence compliance = amber (needs review)
                status = ComplianceStatus.AMBER

        # Determine if professional review is required
        requires_review = (
            status == ComplianceStatus.AMBER
            or status == ComplianceStatus.RED
            or confidence < amber_threshold
        )

        # Assign priority level
        priority = self._assign_priority(status, confidence, is_compliant)

        # Create scored finding
        scored_finding = {
            **finding,  # Include original finding data
            "traffic_light_status": status.value,
            "confidence_percentage": round(confidence, 2),
            "requires_professional_review": requires_review,
            "priority": priority,
            "status_emoji": self._get_emoji(status),
            "status_description": self._get_status_description(status, confidence, is_compliant),
        }

        return scored_finding

    def _calculate_overall_status(self, scored_findings: List[Dict[str, Any]]) -> str:
        """
        Calculate overall document compliance status.

        Rules:
        - If ANY finding is RED → Overall is RED
        - If no RED but ANY AMBER → Overall is AMBER
        - If all GREEN → Overall is GREEN
        """
        if not scored_findings:
            return ComplianceStatus.AMBER.value  # No findings = needs review

        statuses = [f["traffic_light_status"] for f in scored_findings]

        if ComplianceStatus.RED.value in statuses:
            return ComplianceStatus.RED.value
        elif ComplianceStatus.AMBER.value in statuses:
            return ComplianceStatus.AMBER.value
        else:
            return ComplianceStatus.GREEN.value

    def _generate_statistics(self, scored_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistical summary of findings.
        """
        if not scored_findings:
            return {
                "green_count": 0,
                "amber_count": 0,
                "red_count": 0,
                "total": 0,
                "compliance_rate": 0,
                "average_confidence": 0,
                "requires_review_count": 0,
            }

        green_count = sum(
            1 for f in scored_findings if f["traffic_light_status"] == ComplianceStatus.GREEN.value
        )
        amber_count = sum(
            1 for f in scored_findings if f["traffic_light_status"] == ComplianceStatus.AMBER.value
        )
        red_count = sum(
            1 for f in scored_findings if f["traffic_light_status"] == ComplianceStatus.RED.value
        )

        total = len(scored_findings)
        compliance_rate = (green_count / total * 100) if total > 0 else 0

        average_confidence = (
            sum(f["confidence_percentage"] for f in scored_findings) / total
            if total > 0
            else 0
        )

        requires_review_count = sum(
            1 for f in scored_findings if f["requires_professional_review"]
        )

        return {
            "green_count": green_count,
            "amber_count": amber_count,
            "red_count": red_count,
            "total": total,
            "compliance_rate": round(compliance_rate, 2),
            "average_confidence": round(average_confidence, 2),
            "requires_review_count": requires_review_count,
            "green_percentage": round((green_count / total * 100), 2) if total > 0 else 0,
            "amber_percentage": round((amber_count / total * 100), 2) if total > 0 else 0,
            "red_percentage": round((red_count / total * 100), 2) if total > 0 else 0,
        }

    def _assign_priority(self, status: ComplianceStatus, confidence: float, is_compliant: bool) -> str:
        """
        Assign priority level: critical, high, medium, low.
        """
        if status == ComplianceStatus.RED:
            if confidence >= 85:
                return "critical"  # High confidence non-compliance
            else:
                return "high"  # Lower confidence non-compliance
        elif status == ComplianceStatus.AMBER:
            if not is_compliant:
                return "high"  # Non-compliant but low confidence
            else:
                return "medium"  # Compliant but needs review
        else:
            return "low"  # Green status, compliant

    def _get_emoji(self, status: ComplianceStatus) -> str:
        """Get emoji for traffic light status."""
        emoji_map = {
            ComplianceStatus.GREEN: "🟢",
            ComplianceStatus.AMBER: "🟡",
            ComplianceStatus.RED: "🔴",
        }
        return emoji_map.get(status, "⚪")

    def _get_status_description(
        self, status: ComplianceStatus, confidence: float, is_compliant: bool
    ) -> str:
        """Get human-readable status description."""
        if status == ComplianceStatus.GREEN:
            return f"Compliant with high confidence ({confidence:.0f}%)"
        elif status == ComplianceStatus.AMBER:
            if is_compliant:
                return f"Appears compliant but requires professional review ({confidence:.0f}% confidence)"
            else:
                return f"Potential non-compliance - requires professional review ({confidence:.0f}% confidence)"
        else:  # RED
            if confidence >= 85:
                return f"Non-compliant - immediate action required ({confidence:.0f}% confidence)"
            else:
                return f"Likely non-compliant - professional review urgently required ({confidence:.0f}% confidence)"

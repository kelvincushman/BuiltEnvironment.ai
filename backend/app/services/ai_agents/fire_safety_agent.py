"""
Fire Safety AI Agent using LangGraph for compliance checking.
Analyzes documents against UK Building Regulations Part B (Fire Safety).
"""

from typing import Dict, Any, List, TypedDict, Annotated
import operator
from anthropic import AsyncAnthropic
from langgraph.graph import StateGraph, END

from ...core.config import settings


class AgentState(TypedDict):
    """
    State that flows through the LangGraph workflow.
    """

    # Input
    document_text: str
    document_metadata: Dict[str, Any]

    # Analysis state
    document_summary: str
    identified_sections: List[Dict[str, str]]
    compliance_findings: List[Dict[str, Any]]

    # Output
    overall_status: str  # green, amber, red
    confidence_score: float
    reasoning: str

    # Accumulator for messages
    messages: Annotated[List[str], operator.add]


class FireSafetyAgent:
    """
    AI Agent for analyzing fire safety compliance using Part B regulations.
    Uses LangGraph for orchestration and Claude for analysis.
    """

    def __init__(self):
        """Initialize the agent with Claude client."""
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

        # UK Building Regulations Part B - Fire Safety key requirements
        self.part_b_requirements = {
            "B1": {
                "title": "Means of warning and escape",
                "requirements": [
                    "Adequate means of escape in case of fire",
                    "Fire detection and warning systems",
                    "Protected escape routes",
                    "Travel distances to exits",
                ],
            },
            "B2": {
                "title": "Internal fire spread (linings)",
                "requirements": [
                    "Wall and ceiling linings classification",
                    "Fire resistance of materials",
                    "Thermoplastic materials restrictions",
                ],
            },
            "B3": {
                "title": "Internal fire spread (structure)",
                "requirements": [
                    "Fire resistance of structural elements",
                    "Compartmentation",
                    "Protected shafts and protected stairways",
                    "Cavity barriers and fire stopping",
                ],
            },
            "B4": {
                "title": "External fire spread",
                "requirements": [
                    "External walls fire resistance",
                    "Roof construction and covering",
                    "Space separation between buildings",
                ],
            },
            "B5": {
                "title": "Access and facilities for the fire service",
                "requirements": [
                    "Fire service vehicle access",
                    "Fire mains and hydrants",
                    "Venting of heat and smoke",
                ],
            },
        }

    async def _call_claude(self, messages: List[Dict[str, str]], max_tokens: int = 2000) -> str:
        """Helper to call Claude API."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages,
        )
        return response.content[0].text

    async def analyze_document_summary(self, state: AgentState) -> AgentState:
        """
        Step 1: Analyze document and create summary.
        """
        prompt = f"""Analyze this building document and provide a concise summary focusing on fire safety aspects.

Document:
{state["document_text"][:5000]}  # First 5000 chars

Provide:
1. Document type (e.g., Fire Safety Strategy, Building Control submission, etc.)
2. Building type and use (e.g., residential, commercial, height, occupancy)
3. Key fire safety systems mentioned
4. Overall fire safety approach

Be concise and factual."""

        summary = await self._call_claude([{"role": "user", "content": prompt}])

        return {
            **state,
            "document_summary": summary,
            "messages": ["✅ Document summary completed"],
        }

    async def identify_sections(self, state: AgentState) -> AgentState:
        """
        Step 2: Identify relevant sections for Part B compliance.
        """
        prompt = f"""Based on this document summary and the full text, identify specific sections that relate to UK Building Regulations Part B (Fire Safety).

Summary:
{state["document_summary"]}

Full text (first 10,000 characters):
{state["document_text"][:10000]}

For each relevant section found, provide:
- Section title/number
- Brief description
- Which Part B requirement it addresses (B1-B5)

Format as JSON array:
[
  {{
    "section": "Section 3.2",
    "description": "Fire alarm and detection system",
    "part_b_reference": "B1"
  }}
]

If no specific sections are clearly marked, describe the relevant content areas."""

        sections_json = await self._call_claude([{"role": "user", "content": prompt}])

        # Parse JSON (in production, add error handling)
        try:
            import json
            sections = json.loads(sections_json)
        except:
            sections = []

        return {
            **state,
            "identified_sections": sections,
            "messages": ["✅ Identified relevant sections"],
        }

    async def check_compliance(self, state: AgentState) -> AgentState:
        """
        Step 3: Check compliance for each Part B requirement.
        """
        findings = []

        # Check each Part B requirement
        for req_id, req_data in self.part_b_requirements.items():
            prompt = f"""Analyze this document for compliance with UK Building Regulations Part {req_id}: {req_data["title"]}.

Document Summary:
{state["document_summary"]}

Requirements to check:
{chr(10).join(f"- {req}" for req in req_data["requirements"])}

Identified Sections:
{chr(10).join(f"- {sec.get('section', 'N/A')}: {sec.get('description', 'N/A')}" for sec in state["identified_sections"])}

Relevant document excerpt (search the full text for Part {req_id} references):
{state["document_text"][:8000]}

Provide:
1. Status: GREEN (clearly compliant), AMBER (partially addressed/needs clarification), or RED (non-compliant/missing)
2. Confidence: 0.0-1.0 (how confident are you in this assessment)
3. Evidence: Specific quotes or references from the document
4. Issues: List any gaps, concerns, or missing information
5. Recommendations: What should be done to achieve full compliance

Format as JSON:
{{
  "status": "green|amber|red",
  "confidence": 0.85,
  "evidence": "Document states...",
  "issues": ["Issue 1", "Issue 2"],
  "recommendations": ["Recommendation 1"]
}}"""

            finding_json = await self._call_claude([{"role": "user", "content": prompt}], max_tokens=1000)

            try:
                import json
                finding = json.loads(finding_json)
                finding["requirement_id"] = req_id
                finding["requirement_title"] = req_data["title"]
                findings.append(finding)
            except Exception as e:
                # Fallback if JSON parsing fails
                findings.append({
                    "requirement_id": req_id,
                    "requirement_title": req_data["title"],
                    "status": "amber",
                    "confidence": 0.5,
                    "evidence": finding_json[:200],
                    "issues": ["Could not parse analysis"],
                    "recommendations": ["Manual review required"],
                })

        return {
            **state,
            "compliance_findings": findings,
            "messages": ["✅ Compliance analysis completed"],
        }

    async def determine_overall_status(self, state: AgentState) -> AgentState:
        """
        Step 4: Determine overall compliance status.
        """
        findings = state["compliance_findings"]

        # Count status types
        status_counts = {"green": 0, "amber": 0, "red": 0}
        total_confidence = 0

        for finding in findings:
            status = finding.get("status", "amber").lower()
            status_counts[status] = status_counts.get(status, 0) + 1
            total_confidence += finding.get("confidence", 0.5)

        avg_confidence = total_confidence / len(findings) if findings else 0.5

        # Determine overall status
        if status_counts["red"] > 0:
            overall_status = "red"
            reasoning = f"Found {status_counts['red']} non-compliant requirements that must be addressed."
        elif status_counts["amber"] > 2:
            overall_status = "amber"
            reasoning = f"Found {status_counts['amber']} requirements needing clarification or additional information."
        elif status_counts["amber"] > 0:
            overall_status = "amber"
            reasoning = f"Mostly compliant, but {status_counts['amber']} requirements need review."
        else:
            overall_status = "green"
            reasoning = "All Part B fire safety requirements appear to be adequately addressed."

        return {
            **state,
            "overall_status": overall_status,
            "confidence_score": avg_confidence,
            "reasoning": reasoning,
            "messages": ["✅ Overall assessment completed"],
        }

    def build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        """
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("analyze_summary", self.analyze_document_summary)
        workflow.add_node("identify_sections", self.identify_sections)
        workflow.add_node("check_compliance", self.check_compliance)
        workflow.add_node("determine_status", self.determine_overall_status)

        # Define edges
        workflow.set_entry_point("analyze_summary")
        workflow.add_edge("analyze_summary", "identify_sections")
        workflow.add_edge("identify_sections", "check_compliance")
        workflow.add_edge("check_compliance", "determine_status")
        workflow.add_edge("determine_status", END)

        return workflow.compile()

    async def analyze(self, document_text: str, document_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a document for Part B fire safety compliance.

        Args:
            document_text: Full extracted text from document
            document_metadata: Document metadata (filename, type, etc.)

        Returns:
            Complete compliance analysis with findings and recommendations
        """
        # Initialize state
        initial_state: AgentState = {
            "document_text": document_text,
            "document_metadata": document_metadata,
            "document_summary": "",
            "identified_sections": [],
            "compliance_findings": [],
            "overall_status": "amber",
            "confidence_score": 0.0,
            "reasoning": "",
            "messages": [],
        }

        # Build and run graph
        graph = self.build_graph()
        final_state = await graph.ainvoke(initial_state)

        # Format response
        return {
            "agent_type": "fire_safety",
            "agent_version": "1.0.0",
            "model_used": self.model,
            "overall_status": final_state["overall_status"],
            "confidence_score": final_state["confidence_score"],
            "reasoning": final_state["reasoning"],
            "document_summary": final_state["document_summary"],
            "identified_sections": final_state["identified_sections"],
            "compliance_findings": final_state["compliance_findings"],
            "messages": final_state["messages"],
            "part_b_coverage": {
                "B1": "Means of warning and escape",
                "B2": "Internal fire spread (linings)",
                "B3": "Internal fire spread (structure)",
                "B4": "External fire spread",
                "B5": "Access and facilities for fire service",
            },
        }

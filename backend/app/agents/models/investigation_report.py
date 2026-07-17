from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.agents.models.agent_result import AgentResult

class InvestigationReport(BaseModel):
    """The final executive summary report aggregating all findings and recommendations from the multi-agent investigation."""

    investigation_id: str
    transaction_id: str
    overall_risk: str  # e.g., "LOW", "MEDIUM", "HIGH"
    overall_confidence: float
    executive_summary: str = ""
    findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    executed_agents: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_agent_result(self, result: AgentResult) -> None:
        """Integrates the findings and recommendation outputs from an executed AgentResult into the report."""
        if result.agent_name not in self.executed_agents:
            self.executed_agents.append(result.agent_name)
        
        # Merge findings and recommendations
        for finding in result.findings:
            if finding not in self.findings:
                self.findings.append(finding)
                
        for rec in result.recommendations:
            if rec not in self.recommendations:
                self.recommendations.append(rec)
                
        # Merge evidence items
        for ev in result.evidence:
            self.evidence.append(ev)

    def generate_summary(self, summary_text: str) -> None:
        """Updates the executive overview summary text block."""
        self.executive_summary = summary_text

    def export_dict(self) -> Dict[str, Any]:
        """Exports the full investigation report into a standard dictionary schema."""
        data = self.model_dump()
        if isinstance(data.get("generated_at"), datetime):
            data["generated_at"] = data["generated_at"].isoformat()
        elif "generated_at" in data and hasattr(data["generated_at"], "isoformat"):
            data["generated_at"] = data["generated_at"].isoformat()
        return data

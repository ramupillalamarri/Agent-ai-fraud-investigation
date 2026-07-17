from typing import TypedDict, List, Dict, Any, Optional
from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.agent_result import AgentResult
from app.agents.models.investigation_report import InvestigationReport

class InvestigationState(TypedDict):
    """Represents the complete state schema shared between all multi-agent node executions."""
    
    context: InvestigationContext
    report: Optional[InvestigationReport]
    agent_results: List[AgentResult]
    evidence: List[Dict[str, Any]]
    recommendations: List[str]
    execution_metadata: Dict[str, Any]
    next_node: str

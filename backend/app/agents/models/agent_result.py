import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AgentResult(BaseModel):
    """Contains the evaluation findings, recommendations, and execution metrics of an individual agent."""

    agent_name: str
    status: str  # e.g., "SUCCESS", "FAILED", "SKIPPED"
    confidence_score: float
    findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    execution_time_ms: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the agent result into a standard Python dictionary."""
        return self.model_dump()

    def to_json(self, indent: Optional[int] = None) -> str:
        """Serializes the agent result into a valid JSON string."""
        return self.model_dump_json(indent=indent)

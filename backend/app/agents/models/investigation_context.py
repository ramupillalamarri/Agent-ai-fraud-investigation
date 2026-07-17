from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class InvestigationContext(BaseModel):
    """Core data contract representing the state and memory of a fraud investigation workflow.
    
    Shared across all autonomous AI agents participating in the investigation.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    investigation_id: str
    transaction_id: str
    transaction_data: Dict[str, Any]
    prediction_result: Dict[str, Any]
    fraud_probability: float
    risk_score: int
    priority: str  # e.g., "LOW", "MEDIUM", "HIGH"
    investigation_status: str = "PENDING"  # e.g., "PENDING", "RUNNING", "COMPLETED", "FAILED"
    investigation_started_at: datetime = Field(default_factory=datetime.utcnow)
    investigation_completed_at: Optional[datetime] = None
    executed_agents: List[str] = Field(default_factory=list)
    shared_memory: Dict[str, Any] = Field(default_factory=dict)
    collected_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_evidence(self, agent_name: str, key_finding: str, details: Any, confidence: float = 1.0) -> None:
        """Adds a piece of verified evidence collected by an agent."""
        evidence_item = {
            "agent_name": agent_name,
            "key_finding": key_finding,
            "details": details,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.collected_evidence.append(evidence_item)

    def update_shared_memory(self, key: str, value: Any) -> None:
        """Updates the shared memory workspace with intermediate findings."""
        self.shared_memory[key] = value

    def mark_agent_executed(self, agent_name: str) -> None:
        """Registers that a specific agent has completed its execution round."""
        if agent_name not in self.executed_agents:
            self.executed_agents.append(agent_name)

    def complete_investigation(self, status: str = "COMPLETED") -> None:
        """Marks the investigation context execution flow as finished."""
        self.investigation_status = status
        self.investigation_completed_at = datetime.utcnow()

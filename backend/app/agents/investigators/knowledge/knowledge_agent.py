import logging
from typing import List, Optional
from app.agents.base.base_agent import BaseAgent
from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.agent_result import AgentResult
from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.services.retrieval_service import RetrievalService

logger = logging.getLogger("app.agents.KnowledgeAgent")

class KnowledgeAgent(BaseAgent):
    """Orchestrates RAG pipelines to retrieve context from compliance playbooks, SOPs, and manuals."""

    def __init__(
        self,
        agent_id: str = "knowledge-investigator-01",
        agent_name: str = "KnowledgeAgent",
        description: str = "Retrieves relevant regulatory rules and SOP documents matching fraud anomalies.",
        version: str = "1.0.0",
        enabled: bool = True,
        execution_priority: int = 50,
        supported_features: Optional[List[str]] = None,
        config: Optional[KnowledgeAgentConfig] = None,
        retrieval_service: Optional[RetrievalService] = None
    ) -> None:
        """Initializes the KnowledgeAgent with configuration settings and retrieval orchestration services."""
        super().__init__(
            agent_id=agent_id,
            agent_name=agent_name,
            description=description,
            version=version,
            enabled=enabled,
            execution_priority=execution_priority,
            supported_features=supported_features or ["knowledge", "rag", "sop_search"]
        )
        self.config = config or KnowledgeAgentConfig()
        self.retrieval_service = retrieval_service

    def validate(self, context: InvestigationContext) -> None:
        """Enforces validation checks on the context anomalies query parameters."""
        tx_data = context.transaction_data or {}
        if not tx_data:
            raise ValueError("KnowledgeAgent requires transaction_data payload inside execution context.")

    def health_check(self) -> bool:
        """Checks RAG pipeline services dependencies and config variables."""
        if not isinstance(self.config, KnowledgeAgentConfig):
            logger.error("Health check failed: Invalid configuration class instance type.")
            return False
        return True

    def _execute(self, context: InvestigationContext) -> AgentResult:
        """Protected core execution pipeline retrieving and attaching RAG context findings to the report."""
        import time
        logger.info("Knowledge Agent started")
        
        start_time = time.perf_counter()
        
        # 1. Validation
        self.validate(context)
        
        findings = []
        recommendations = []
        evidence = []
        
        # Mock / Skeleton execution (to be replaced with actual RAG retrieval service integration)
        if self.retrieval_service:
            # e.g., query generated from transaction anomaly features
            query_str = f"Identify compliance rules for transaction amount ${context.transaction_data.get('amount', 0.0)}"
            retrieved = self.retrieval_service.retrieve_context(query_str, self.config.top_k)
            
            for chunk in retrieved.retrieved_chunks:
                evidence.append({
                    "type": "KnowledgeReference",
                    "severity": "LOW",
                    "title": f"Reference from: {chunk.document_id}",
                    "description": chunk.content,
                    "confidence": chunk.score,
                    "source": "KnowledgeAgent",
                    "metadata": chunk.metadata
                })
            
            findings.append(f"Retrieved {len(retrieved.retrieved_chunks)} relevant compliance references.")
            recommendations.append("Review standard retail playbooks guidelines")
        else:
            findings.append("No active retrieval service configured. Scaffold execution completed.")
            recommendations.append("Review standard retail playbooks guidelines")
            
        latency = (time.perf_counter() - start_time) * 1000.0
        logger.info("Knowledge Agent completed in %.2fms", latency)

        return AgentResult(
            agent_name=self.agent_name,
            status="SUCCESS",
            confidence_score=1.0,
            findings=findings,
            recommendations=recommendations,
            evidence=evidence,
            execution_time_ms=int(latency),
            metadata={
                "retrieved_context_count": len(evidence),
                "retrieval_enabled": self.retrieval_service is not None
            }
        )

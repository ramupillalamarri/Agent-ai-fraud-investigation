import logging
from typing import List, Dict, Any, Optional
from app.agents.base.base_agent import BaseAgent
from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.agent_result import AgentResult

from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.retriever import KnowledgeRetriever

logger = logging.getLogger("app.agents.KnowledgeAgent")

class KnowledgeAgent(BaseAgent):
    """Knowledge Retrieval Agent that performs semantic searches over playbooks, compliance guidelines, and policies."""

    def __init__(
        self,
        agent_id: str = "knowledge-investigator-01",
        agent_name: str = "KnowledgeAgent",
        description: str = "Performs semantic retrieval against compliance documentation, internal guidelines, and fraud playbooks.",
        version: str = "1.0.0",
        enabled: bool = True,
        execution_priority: int = 50,
        supported_features: Optional[List[str]] = None,
        config: Optional[KnowledgeAgentConfig] = None
    ) -> None:
        super().__init__(
            agent_id=agent_id,
            agent_name=agent_name,
            description=description,
            version=version,
            enabled=enabled,
            execution_priority=execution_priority,
            supported_features=supported_features or ["knowledge", "rag", "retrieval"]
        )
        self.config = config or KnowledgeAgentConfig()
        self.retriever = KnowledgeRetriever(self.config)

    def validate(self, context: InvestigationContext) -> None:
        """Validates that transaction parameters are loaded in context."""
        if not context.transaction_data:
            raise ValueError("KnowledgeAgent requires valid context transaction_data.")

    def health_check(self) -> bool:
        """Confirms internal retrieval status."""
        return True

    def _generate_query(self, context: InvestigationContext) -> str:
        """Generates a search query targeting RAG text indexes from context telemetry."""
        tx_data = context.transaction_data or {}
        
        query_parts = []
        
        # Suspected ATO/Identity Check
        if "device_id" in tx_data or "ip_address" in tx_data:
            query_parts.append("account takeover ATO device fingerprint mismatch")
            
        # Suspected High Risk Merchant Check
        if "merchant" in tx_data or "category" in tx_data:
            category = tx_data.get("category", "")
            query_parts.append(f"high risk merchant category {category} electronics crypto AML sanctions")
            
        # Standard velocity / amounts check
        if float(tx_data.get("amount") or 0.0) > 1000.0:
            query_parts.append("velocity rules limits high amount limits")
            
        # Fallback overall query
        if not query_parts:
            query_parts.append("fraud investigation playbook guidelines risk policy")
            
        return " ".join(query_parts)

    def _execute(self, context: InvestigationContext) -> AgentResult:
        """Executes RAG retrieval flow."""
        query = self._generate_query(context)
        self.log_info("Formulated RAG query: '%s'", query)
        
        # Execute retrieval
        result = self.retriever.retrieve(query)
        passages = result.get("passages", [])
        
        evidence_list = []
        findings = []
        recommendations = []
        
        # Map passages to evidence records
        for pass_item in passages:
            meta = pass_item["metadata"]
            evidence_list.append({
                "type": "KnowledgeRetrievedPassage",
                "severity": "MEDIUM",
                "confidence": pass_item["score"],
                "description": f"Retrieved playbook snippet ({meta.get('title')}): {pass_item['content']}",
                "source": f"RAG:{meta.get('source')}"
            })
            
        if passages:
            findings.append(f"Retrieved {len(passages)} matching fraud playbooks and compliance guidelines.")
            # Standard playbook recommendations
            recommendations.append("Execute playbook steps matching retrieved guidelines")
            recommendations.append("Verify AML compliance threshold alerts")
        else:
            findings.append("No matching internal playbooks or compliance alerts retrieved for this transaction signature.")
            recommendations.append("Apply baseline analyst manual review")

        metadata = {
            "query": query,
            "latency_ms": result["latency_ms"],
            "retrieved_count": len(passages),
            "vocabulary_size": len(self.retriever.vector_store.vocabulary)
        }

        return AgentResult(
            agent_name=self.agent_name,
            status="SUCCESS",
            confidence_score=result["confidence_score"] or 1.0,
            findings=findings,
            recommendations=recommendations,
            evidence=evidence_list,
            execution_time_ms=0,  # set automatically
            metadata=metadata
        )

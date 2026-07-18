import logging
import time
from typing import List, Optional, Dict, Any
from app.agents.base.base_agent import BaseAgent
from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.agent_result import AgentResult
from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.services.retrieval_service import RetrievalService

logger = logging.getLogger("app.agents.investigators.knowledge.knowledge_agent")

class KnowledgeAgent(BaseAgent):
    """Orchestrates RAG pipelines to retrieve domain knowledge (SOPs, Playbooks, Compliance) matching investigation contexts."""

    def __init__(
        self,
        agent_id: str = "knowledge-investigator-01",
        agent_name: str = "KnowledgeAgent",
        description: str = "Retrieves relevant compliance policies, SOPs, and historical cases for fraud investigations.",
        version: str = "1.0.0",
        enabled: bool = True,
        execution_priority: int = 50,
        supported_features: Optional[List[str]] = None,
        config: Optional[KnowledgeAgentConfig] = None,
        retrieval_service: Optional[RetrievalService] = None
    ) -> None:
        super().__init__(
            agent_id=agent_id,
            agent_name=agent_name,
            description=description,
            version=version,
            enabled=enabled,
            execution_priority=execution_priority,
            supported_features=supported_features or ["knowledge", "rag", "compliance_search"]
        )
        self.config = config or KnowledgeAgentConfig()
        self.retrieval_service = retrieval_service

    def validate(self, context: InvestigationContext) -> None:
        """Enforces validation checks on the execution context transaction data payload."""
        tx_data = context.transaction_data or {}
        if not tx_data:
            raise ValueError("KnowledgeAgent validation failed: transaction_data is missing inside context.")

    def health_check(self) -> bool:
        """Verifies operational state of retrieval service, retrievers, vector stores, and embedding providers."""
        logger.info("Health check started")
        try:
            if not isinstance(self.config, KnowledgeAgentConfig):
                logger.error("Health check failed: Invalid configuration class instance type.")
                return False
            if not self.retrieval_service:
                logger.error("Health check failed: RetrievalService is not initialized.")
                return False
            if not self.retrieval_service.hybrid_retriever:
                logger.error("Health check failed: HybridRetriever is missing inside retrieval service.")
                return False
            
            # Check vector store provider health check state
            semantic = self.retrieval_service.hybrid_retriever.semantic_retriever
            if not semantic or not semantic.vector_store_provider:
                logger.error("Health check failed: Semantic vector store provider is not initialized.")
                return False
            if not semantic.vector_store_provider.health_check():
                logger.error("Health check failed: Underlyling vector database reported unhealthy state.")
                return False

            logger.info("Health check completed: all services reporting healthy state.")
            return True
        except Exception as e:
            logger.error("Health check failed with unexpected exception: %s", str(e))
            return False

    def _execute(self, context: InvestigationContext) -> AgentResult:
        """Core execution pipeline retrieving and attaching RAG context findings to the report."""
        logger.info("KnowledgeAgent started")
        start_time = time.perf_counter()

        # 1. Validation
        self.validate(context)

        findings = []
        recommendations = []
        evidence = []

        if not self.retrieval_service:
            logger.warning("No active retrieval service configured. Scaffold execution completed.")
            findings.append("RAG retrieval service not configured. Execution bypassed.")
            return AgentResult(
                agent_name=self.agent_name,
                status="SKIPPED",
                confidence_score=0.0,
                findings=findings,
                recommendations=["Configure a valid RetrievalService instance"],
                evidence=[],
                execution_time_ms=int((time.perf_counter() - start_time) * 1000),
                metadata={"reason": "retrieval_service_missing"}
            )

        # 2. Query Builder: Generate multi-queries from InvestigationContext and child agent findings
        queries = self.retrieval_service.query_builder.build_queries(context)
        logger.info("Generated %d search queries from investigation context", len(queries))

        # 3. Invoke Retrieval Service (gather context matching generated queries)
        unique_chunks = {}
        for query in queries:
            # Gather top_k chunks for each query
            retrieved = self.retrieval_service.retrieve_context(query, self.config.top_k)
            for chunk in retrieved.retrieved_chunks:
                unique_chunks[chunk.chunk_id] = chunk

        # 4. Score and sort combined chunks
        sorted_chunks = sorted(unique_chunks.values(), key=lambda x: x.score, reverse=True)
        top_chunks = sorted_chunks[:self.config.top_k]
        logger.info("Knowledge retrieved: matched %d unique chunks from vector store", len(top_chunks))

        # 5. Convert retrieved chunks into structured Evidence and Recommendations
        for idx, chunk in enumerate(top_chunks):
            meta = chunk.metadata or {}
            
            # Map evidence record
            evidence_item = {
                "evidence_id": f"ev_knowledge_{chunk.chunk_id}",
                "title": f"Reference from: {meta.get('title', 'Document')}",
                "description": chunk.content,
                "confidence": chunk.score,
                "source_document": meta.get("source", "unknown"),
                "chunk_reference": chunk.chunk_id,
                "category": meta.get("category", "compliance"),
                "section": meta.get("section", "Introduction"),
                "page_number": meta.get("page_number", 1)
            }
            evidence.append(evidence_item)
            
            # Append finding statements
            findings.append(
                f"Matched compliance guideline from '{meta.get('title', 'Document')}' "
                f"under section '{meta.get('section', 'Introduction')}' (score={chunk.score:.2f})."
            )

        # 6. Generate retrieval-based recommendations
        for chunk in top_chunks:
            meta = chunk.metadata or {}
            category = meta.get("category", "")
            
            if category == "fraud_playbooks":
                recommendations.append("Compare findings against current retail playbooks SOP parameters.")
            elif category == "aml":
                recommendations.append("Execute name match comparison against updated sanctions list databases.")
            elif category == "pci_dss":
                recommendations.append("Verify primary cardholder account data masks are applied on UI interfaces.")
            elif category == "merchant_policies":
                recommendations.append("Review merchant signature checkups on transaction receipt files.")
            elif category == "historical_cases":
                recommendations.append("Compare current transaction details with historical chargeback anomalies patterns.")
            elif category == "compliance":
                recommendations.append("Execute customer identity verification procedures on user records.")


        # Default fallback recommendations if none match
        if not recommendations:
            recommendations.append("Perform manual compliance review on transaction flags.")
        else:
            # Deduplicate recommendations
            recommendations = list(dict.fromkeys(recommendations))

        latency = (time.perf_counter() - start_time) * 1000.0
        logger.info("Evidence generated. KnowledgeAgent completed in %.2fms", latency)

        # Calculate average confidence
        avg_confidence = sum(c.score for c in top_chunks) / len(top_chunks) if top_chunks else 1.0

        return AgentResult(
            agent_name=self.agent_name,
            status="SUCCESS",
            confidence_score=round(avg_confidence, 2),
            findings=findings,
            recommendations=recommendations,
            evidence=evidence,
            execution_time_ms=int(latency),
            metadata={
                "retrieved_documents_count": len(top_chunks),
                "unique_sources": list(set(c.metadata.get("source", "unknown") for c in top_chunks)),
                "retrieval_strategy": "hybrid",
                "retrieval_queries": queries,
                "latency_ms": latency
            }
        )
export_agent = KnowledgeAgent

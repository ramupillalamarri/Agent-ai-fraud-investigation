import sys
import os
import pytest
from datetime import datetime
from typing import List, Dict, Any

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.providers.embedding_provider import EmbeddingProvider
from app.agents.investigators.knowledge.providers.chromadb_provider import ChromaDBProvider
from app.agents.investigators.knowledge.retrievers.semantic_retriever import SemanticRetriever
from app.agents.investigators.knowledge.retrievers.metadata_retriever import MetadataRetriever
from app.agents.investigators.knowledge.retrievers.hybrid_retriever import HybridRetriever
from app.agents.investigators.knowledge.services.retrieval_service import RetrievalService
from app.agents.investigators.knowledge.knowledge_agent import KnowledgeAgent
from app.agents.models.investigation_context import InvestigationContext
from app.agents.base.base_agent import BaseAgent
from app.agents.models.agent_result import AgentResult
from app.agents.orchestrator.registry import AgentRegistry
from app.agents.orchestrator.orchestrator import InvestigationOrchestrator

# 1. Mock providers
class MockEmbeddingProvider(EmbeddingProvider):
    def embed_query(self, text: str) -> List[float]:
        return [0.1, 0.9, 0.0]
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1, 0.9, 0.0] for _ in texts]

class DummyAgent(BaseAgent):
    def _execute(self, context: InvestigationContext) -> AgentResult:
        context.add_evidence(self.agent_name, "Verified key flag", {"flag": True})
        return self.create_success_result(
            findings=["Findings from dummy agent."],
            recommendations=["Escalate standard procedure."],
            evidence=[{"flag": True}]
        )
    def validate(self, context: InvestigationContext) -> None:
        pass
    def health_check(self) -> bool:
        return True

class FailingDummyAgent(BaseAgent):
    def _execute(self, context: InvestigationContext) -> AgentResult:
        raise ValueError("Simulated pipeline validation/runtime crash.")
    def validate(self, context: InvestigationContext) -> None:
        pass
    def health_check(self) -> bool:
        return False

@pytest.fixture
def orchestration_setup():
    registry = AgentRegistry()
    
    # Register customer dummy and knowledge agent
    cust = DummyAgent("cust-01", "CustomerAgent", "Customer checks", "1.0", execution_priority=1)
    registry.register(cust)
    
    # Configure and register KnowledgeAgent
    config = KnowledgeAgentConfig(similarity_threshold=0.35, collection_name="integration_collection")
    embedding_provider = MockEmbeddingProvider()
    vector_store_provider = ChromaDBProvider(config)
    
    # Ingest mock compliance rules
    vector_store_provider.add_vectors(
        ids=["c1"],
        vectors=[[0.1, 0.9, 0.0]],
        documents=["SOP: Compliance verification must check customer Watchlists."],
        metadatas=[{"document_id": "doc_comp", "category": "compliance", "source": "sop.txt", "title": "SOP Compliance", "created_at": datetime.utcnow().isoformat()}]
    )
    
    semantic_retriever = SemanticRetriever(embedding_provider, vector_store_provider, config.similarity_threshold)
    metadata_retriever = MetadataRetriever(embedding_provider, vector_store_provider)
    hybrid_retriever = HybridRetriever(semantic_retriever, metadata_retriever)
    retrieval_service = RetrievalService(config, hybrid_retriever)
    
    knowledge_agent = KnowledgeAgent(agent_id="know-01", agent_name="KnowledgeAgent", config=config, retrieval_service=retrieval_service, execution_priority=5)
    registry.register(knowledge_agent)
    
    orchestrator = InvestigationOrchestrator(registry)
    return orchestrator, registry, knowledge_agent

def test_complete_investigation_success(orchestration_setup):
    """Verify that a standard execution loop runs all registered agents and merges RAG metadata."""
    orchestrator, registry, knowledge_agent = orchestration_setup
    
    context = InvestigationContext(
        investigation_id="INV-INT-01",
        transaction_id="TX-INT-01",
        transaction_data={"amount": 350.0, "currency": "USD", "category": "retail"},
        prediction_result={"prediction": "Legitimate", "probability": 0.02},
        fraud_probability=0.02,
        risk_score=2,
        priority="LOW"
    )
    
    # Overall health check verification
    assert orchestrator.health_check() is True
    
    report = orchestrator.run_investigation(context)
    
    assert report.overall_confidence > 0.0
    # Check that Customer and Knowledge evidence were merged
    assert len(report.executed_agents) == 2
    assert "CustomerAgent" in report.executed_agents
    assert "KnowledgeAgent" in report.executed_agents
    
    # Confirm findings list compilation
    assert any("Compliance verification" in ev.get("description", "") for ev in report.evidence)
    assert any("Escalate standard procedure" in rec for rec in report.recommendations)

def test_knowledge_agent_failure_resilience(orchestration_setup):
    """Verify that a failure inside KnowledgeAgent is captured gracefully, returning a partial report."""
    orchestrator, registry, knowledge_agent = orchestration_setup
    
    # Replace KnowledgeAgent with a failing one
    registry.unregister("know-01")
    failing_knowledge = FailingDummyAgent("know-01", "KnowledgeAgent", "Failing knowledge checks", "1.0", execution_priority=5)
    registry.register(failing_knowledge)
    
    # Health check is now false (due to failing agent)
    assert orchestrator.health_check() is False
    
    context = InvestigationContext(
        investigation_id="INV-INT-02",
        transaction_id="TX-INT-02",
        transaction_data={"amount": 100.0, "currency": "USD", "category": "retail"},
        prediction_result={"prediction": "Legitimate", "probability": 0.05},
        fraud_probability=0.05,
        risk_score=2,
        priority="LOW"
    )
    
    # Execution should not crash
    report = orchestrator.run_investigation(context)
    
    # Successful agent (CustomerAgent) is merged, while failing one is logged
    assert "CustomerAgent" in report.executed_agents
    assert len(report.evidence) == 1
    assert report.overall_confidence > 0.0  # calculated from CustomerAgent success
    
    metrics = context.metadata.get("orchestrator_metrics", {})
    assert "KnowledgeAgent" in metrics.get("failed_agents", [])

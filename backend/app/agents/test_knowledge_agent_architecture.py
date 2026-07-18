import sys
import os
from typing import List, Dict, Any, Optional

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.models.investigation_context import InvestigationContext
from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.knowledge_agent import KnowledgeAgent
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult
from app.agents.investigators.knowledge.providers.embedding_provider import EmbeddingProvider
from app.agents.investigators.knowledge.providers.vector_store_provider import VectorStoreProvider
from app.agents.investigators.knowledge.providers.llm_provider import LLMProvider
from app.agents.investigators.knowledge.retrievers.chunk_retriever import ChunkRetriever
from app.agents.investigators.knowledge.services.retrieval_service import RetrievalService

# 1. Define mock providers implementing the abstract interfaces
class MockEmbeddingProvider(EmbeddingProvider):
    def embed_query(self, text: str) -> List[float]:
        return [0.1, 0.2, 0.3]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]

class MockVectorStoreProvider(VectorStoreProvider):
    def add_vectors(self, ids: List[str], vectors: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]]) -> None:
        pass

    def similarity_search(self, query_vector: List[float], top_k: int) -> List[RetrievalResult]:
        return [
            RetrievalResult(
                document_id="SOP_CHARGEBACK_01",
                chunk_id="chunk_0",
                score=0.95,
                content="Chargeback reversals are authorized when customer signature exists.",
                metadata={"category": "chargeback_policy"}
            )
        ]

    def health_check(self) -> bool:
        return True


class MockLLMProvider(LLMProvider):
    def generate(self, prompt: str, system_instruction: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> str:
        return "SOP rules state that signature matches satisfy customer validation."

# 2. Define verification tests
def test_knowledge_agent_architecture_di():
    """Verify that RAG architecture components can be initialized and dependency-injected successfully."""
    # Instantiation of config and mock providers
    config = KnowledgeAgentConfig(top_k=2)
    embedding_provider = MockEmbeddingProvider()
    vector_store_provider = MockVectorStoreProvider()
    llm_provider = MockLLMProvider()
    
    # DI in retrievers and services
    from app.agents.investigators.knowledge.retrievers.metadata_retriever import MetadataRetriever
    from app.agents.investigators.knowledge.retrievers.hybrid_retriever import HybridRetriever
    from app.agents.investigators.knowledge.retrievers.semantic_retriever import SemanticRetriever
    
    semantic_retriever = SemanticRetriever(embedding_provider, vector_store_provider)
    metadata_retriever = MetadataRetriever(embedding_provider, vector_store_provider)
    hybrid_retriever = HybridRetriever(semantic_retriever, metadata_retriever)
    retrieval_service = RetrievalService(config, hybrid_retriever, llm_provider)

    
    # Inject service into KnowledgeAgent
    agent = KnowledgeAgent(config=config, retrieval_service=retrieval_service)

    
    # Verify health check succeeds
    assert agent.health_check() is True
    
    # Verify validation and execution
    context = InvestigationContext(
        investigation_id="INV-KNOW-001",
        transaction_id="TX-KNOW-001",
        transaction_data={"merchant_id": "merch_01", "amount": 250.0},
        prediction_result={"prediction": "Legitimate", "probability": 0.02},
        fraud_probability=0.02,
        risk_score=2,
        priority="LOW"
    )
    
    result = agent.execute(context)
    
    assert result.status == "SUCCESS"
    assert result.confidence_score > 0.0
    assert len(result.evidence) == 1
    assert result.evidence[0]["title"] == "Reference from: Document"
    assert result.metadata["retrieved_documents_count"] == 1


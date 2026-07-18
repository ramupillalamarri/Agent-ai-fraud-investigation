import sys
import os
import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult
from app.agents.investigators.knowledge.providers.embedding_provider import EmbeddingProvider
from app.agents.investigators.knowledge.providers.chromadb_provider import ChromaDBProvider
from app.agents.investigators.knowledge.retrievers.semantic_retriever import SemanticRetriever
from app.agents.investigators.knowledge.retrievers.metadata_retriever import MetadataRetriever
from app.agents.investigators.knowledge.retrievers.hybrid_retriever import HybridRetriever
from app.agents.investigators.knowledge.services.retrieval_service import RetrievalService
from app.agents.investigators.knowledge.utils.query_builder import QueryBuilder
from app.agents.models.investigation_context import InvestigationContext

# 1. Define mock embedding provider matching key phrases
class MockEmbeddingProvider(EmbeddingProvider):
    def embed_query(self, text: str) -> List[float]:
        text_lower = text.lower()
        if "playbook" in text_lower or "fraud" in text_lower:
            return [0.9, 0.0, 0.0]
        if "aml" in text_lower or "sanctions" in text_lower:
            return [0.0, 0.9, 0.0]
        if "chargeback" in text_lower or "merchant" in text_lower:
            return [0.0, 0.0, 0.9]
        if "pci" in text_lower or "compliance" in text_lower:
            return [0.5, 0.5, 0.0]
        return [0.3, 0.3, 0.3]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]

@pytest.fixture
def retrieval_setup():
    config = KnowledgeAgentConfig(
        similarity_threshold=0.40,
        metadata_boost=0.15,
        recency_weight=0.10
    )
    
    embedding_provider = MockEmbeddingProvider()
    vector_store_provider = ChromaDBProvider(config)
    
    # Pre-populate index with mock documents representing RAG topics
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
    old_date = (datetime.utcnow() - timedelta(days=1000)).isoformat()
    
    docs = [
        # Fraud Playbook PDF
        {
            "ids": ["chunk_playbook_0"],
            "embeddings": [[0.85, 0.0, 0.0]],
            "documents": ["Fraud Playbook guidelines: Reject gift card orders from high risk device fingerprints."],
            "metadatas": [{
                "document_id": "doc_playbook",
                "chunk_id": "chunk_playbook_0",
                "source": "fraud_playbook.pdf",
                "category": "fraud_playbooks",
                "created_at": yesterday
            }]
        },
        # AML Guideline MD
        {
            "ids": ["chunk_aml_0"],
            "embeddings": [[0.0, 0.85, 0.0]],
            "documents": ["AML Sanction verification checks: Match user legal name against sanction lists."],
            "metadatas": [{
                "document_id": "doc_aml",
                "chunk_id": "chunk_aml_0",
                "source": "aml_guide.md",
                "category": "aml",
                "created_at": yesterday
            }]
        },
        # Merchant Policy HTML
        {
            "ids": ["chunk_merchant_0"],
            "embeddings": [[0.0, 0.0, 0.85]],
            "documents": ["Merchant Policy: Reversals are allowed if customer signature is provided."],
            "metadatas": [{
                "document_id": "doc_merchant",
                "chunk_id": "chunk_merchant_0",
                "source": "merchant_rules.html",
                "category": "merchant_policies",
                "created_at": old_date # older file to check recency decay
            }]
        },
        # PCI DSS TXT
        {
            "ids": ["chunk_pci_0"],
            "embeddings": [[0.45, 0.45, 0.0]],
            "documents": ["PCI DSS Standard: Mask primary account numbers when displayed on screen."],
            "metadatas": [{
                "document_id": "doc_pci",
                "chunk_id": "chunk_pci_0",
                "source": "pci_dss.txt",
                "category": "pci_dss",
                "created_at": yesterday
            }]
        }
    ]
    
    for doc in docs:
        vector_store_provider.add_vectors(
            ids=doc["ids"],
            vectors=doc["embeddings"],
            documents=doc["documents"],
            metadatas=doc["metadatas"]
        )
        
    semantic_retriever = SemanticRetriever(embedding_provider, vector_store_provider, config.similarity_threshold)
    metadata_retriever = MetadataRetriever(embedding_provider, vector_store_provider)
    hybrid_retriever = HybridRetriever(semantic_retriever, metadata_retriever)
    
    retrieval_service = RetrievalService(config, hybrid_retriever, query_builder=QueryBuilder())
    
    return config, retrieval_service

def test_search_scenarios(retrieval_setup):
    """Verify that retrieval queries match appropriate document contexts and trigger ranking boosts."""
    config, service = retrieval_setup
    
    # 1. Search Fraud Playbook
    context_playbook = service.retrieve_context("Retrieve active rules for fraud patterns", top_k=1)
    assert len(context_playbook.retrieved_chunks) == 1
    assert context_playbook.retrieved_chunks[0].document_id == "doc_playbook"
    assert "gift card orders" in context_playbook.retrieved_chunks[0].content
    
    # 2. Search AML Guideline
    context_aml = service.retrieve_context("Perform AML verification check", top_k=1)
    assert len(context_aml.retrieved_chunks) == 1
    assert context_aml.retrieved_chunks[0].document_id == "doc_aml"
    assert "sanction lists" in context_aml.retrieved_chunks[0].content
    
    # 3. Search PCI DSS
    context_pci = service.retrieve_context("Mask card compliance under PCI standards", top_k=1)
    assert len(context_pci.retrieved_chunks) == 1
    assert context_pci.retrieved_chunks[0].document_id == "doc_pci"
    assert "primary account numbers" in context_pci.retrieved_chunks[0].content

    # 4. Search Merchant Policy (with category metadata filter)
    context_merchant = service.retrieve_context_filtered("Merchant chargeback requirements", top_k=1, category_filter="merchant_policies")
    assert len(context_merchant.retrieved_chunks) == 1
    assert context_merchant.retrieved_chunks[0].document_id == "doc_merchant"
    assert "signature is provided" in context_merchant.retrieved_chunks[0].content

def test_query_builder_extraction(retrieval_setup):
    """Verify that QueryBuilder builds precise queries from InvestigationContext containing sub-agent findings."""
    config, service = retrieval_setup
    
    # Initialize investigation context with evidence matched from Customer Agent
    context = InvestigationContext(
        investigation_id="INV-RET-01",
        transaction_id="TX-RET-01",
        transaction_data={"amount": 800.0, "currency": "USD", "category": "retail"},
        prediction_result={"prediction": "Suspicious", "probability": 0.65},
        fraud_probability=0.65,
        risk_score=7,
        priority="HIGH"
    )
    # Add child evidence finding
    context.add_evidence(
        agent_name="CustomerAgent",
        key_finding="Name match failure on billing records",
        details="User card name mismatching credit profile."
    )
    
    # Run service using query builder
    generated_queries = service.query_builder.build_queries(context)
    
    assert len(generated_queries) == 2
    assert "Verify rules for transaction amount 800.0" in generated_queries[0]
    assert "Customer verification procedures" in generated_queries[1]

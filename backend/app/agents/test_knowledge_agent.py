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

# Mock Embedding matching target query keywords
class MockEmbeddingProvider(EmbeddingProvider):
    def embed_query(self, text: str) -> List[float]:
        text_lower = text.lower()
        if "customer" in text_lower or "identity" in text_lower:
            return [1.0, 0.0, 0.0, 0.0, 0.0]
        if "merchant" in text_lower or "signature" in text_lower:
            return [0.0, 1.0, 0.0, 0.0, 0.0]
        if "proxy" in text_lower or "network" in text_lower or "device" in text_lower:
            return [0.0, 0.0, 1.0, 0.0, 0.0]
        if "aml" in text_lower or "sanctions" in text_lower:
            return [0.0, 0.0, 0.0, 1.0, 0.0]
        if "pci" in text_lower or "card" in text_lower:
            return [0.0, 0.0, 0.0, 0.0, 1.0]
        return [0.2, 0.2, 0.2, 0.2, 0.2]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]

@pytest.fixture
def agent_setup():
    config = KnowledgeAgentConfig(similarity_threshold=0.35, collection_name="agent_test_collection")
    embedding_provider = MockEmbeddingProvider()
    vector_store_provider = ChromaDBProvider(config)
    
    # Pre-populate index with matching knowledge segments
    now = datetime.utcnow().isoformat()
    docs = [
        # Customer matching chunk
        {
            "ids": ["c1"],
            "embeddings": [[0.95, 0.0, 0.0, 0.0, 0.0]],
            "documents": ["SOP: Customer Identity Match checks. Verify full legal name matches billing record details."],
            "metadatas": [{"document_id": "doc_customer", "category": "compliance", "source": "customer_guide.md", "title": "Customer Verification Guide", "created_at": now}]
        },
        # Merchant matching chunk
        {
            "ids": ["c2"],
            "embeddings": [[0.0, 0.95, 0.0, 0.0, 0.0]],
            "documents": ["Merchant policy: Validate signature matches on all physical checkout receipts."],
            "metadatas": [{"document_id": "doc_merchant", "category": "merchant_policies", "source": "merchant_rules.html", "title": "Merchant Signature Rules", "created_at": now}]
        },
        # Network/Device matching chunk
        {
            "ids": ["c3"],
            "embeddings": [[0.0, 0.0, 0.95, 0.0, 0.0]],
            "documents": ["Fraud Playbooks: Block transactions where IP proxy indicators or device anomalies match velocity limits."],
            "metadatas": [{"document_id": "doc_device", "category": "fraud_playbooks", "source": "fraud_playbook.pdf", "title": "Fraud Detection Playbook", "created_at": now}]
        },
        # AML matching chunk
        {
            "ids": ["c4"],
            "embeddings": [[0.0, 0.0, 0.0, 0.95, 0.0]],
            "documents": ["AML Guidelines: Transactors matching global sanctions listings require instant compliance suspension."],
            "metadatas": [{"document_id": "doc_aml", "category": "aml", "source": "aml_guide.txt", "title": "Global AML Guidelines", "created_at": now}]
        },
        # PCI matching chunk
        {
            "ids": ["c5"],
            "embeddings": [[0.0, 0.0, 0.0, 0.0, 0.95]],
            "documents": ["PCI DSS guidelines: Displayed card numbers must mask all digits except last four digits."],
            "metadatas": [{"document_id": "doc_pci", "category": "pci_dss", "source": "pci_dss.txt", "title": "PCI DSS Compliance Policy", "created_at": now}]
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
    retrieval_service = RetrievalService(config, hybrid_retriever)
    
    agent = KnowledgeAgent(config=config, retrieval_service=retrieval_service)
    
    return agent, vector_store_provider

def test_health_check(agent_setup):
    """Verify that health check executes and verifies underlying dependencies."""
    agent, provider = agent_setup
    assert agent.health_check() is True

def test_customer_fraud_scenario(agent_setup):
    """Verify customer fraud evidence mapping and recommendations."""
    agent, provider = agent_setup
    
    context = InvestigationContext(
        investigation_id="INV-K-CUST",
        transaction_id="TX-K-CUST",
        transaction_data={"amount": 450.0, "currency": "USD", "category": "customer"},
        prediction_result={"prediction": "Legitimate", "probability": 0.01},
        fraud_probability=0.01,
        risk_score=1,
        priority="LOW"
    )
    # Add child evidence finding
    context.add_evidence(
        agent_name="CustomerAgent",
        key_finding="Identity mismatch check flag",
        details="Customer legal profile mismatch."
    )
    
    result = agent.execute(context)
    
    assert result.status == "SUCCESS"
    assert any("Customer Identity Match" in ev["description"] for ev in result.evidence)
    assert any("verification procedures" in rec for rec in result.recommendations)

def test_merchant_fraud_scenario(agent_setup):
    """Verify merchant fraud evidence mapping and recommendations."""
    agent, provider = agent_setup
    
    context = InvestigationContext(
        investigation_id="INV-K-MERCH",
        transaction_id="TX-K-MERCH",
        transaction_data={"amount": 1200.0, "currency": "USD", "category": "merchant"},
        prediction_result={"prediction": "Suspicious", "probability": 0.40},
        fraud_probability=0.40,
        risk_score=5,
        priority="MEDIUM"
    )
    context.add_evidence(
        agent_name="MerchantInvestigationAgent",
        key_finding="High risk merchant check",
        details="Merchant signature verification query."
    )
    
    result = agent.execute(context)
    
    assert result.status == "SUCCESS"
    assert any("signature matches" in ev["description"] for ev in result.evidence)
    assert any("signature checkups" in rec for rec in result.recommendations)

def test_network_and_device_anomalies_scenario(agent_setup):
    """Verify network/device anomalies match standard playbooks guidelines."""
    agent, provider = agent_setup
    
    context = InvestigationContext(
        investigation_id="INV-K-NET",
        transaction_id="TX-K-NET",
        transaction_data={"amount": 80.0, "currency": "USD", "category": "network"},
        prediction_result={"prediction": "Legitimate", "probability": 0.01},
        fraud_probability=0.01,
        risk_score=1,
        priority="LOW"
    )
    context.add_evidence(
        agent_name="DeviceInvestigationAgent",
        key_finding="IP proxy velocity warnings",
        details="Multiple logins from proxy networks."
    )
    
    result = agent.execute(context)
    
    assert result.status == "SUCCESS"
    assert any("IP proxy indicators" in ev["description"] for ev in result.evidence)
    assert any("retail playbooks SOP" in rec for rec in result.recommendations)

def test_aml_and_pci_scenarios(agent_setup):
    """Verify AML and PCI compliance matches."""
    agent, provider = agent_setup
    
    # 1. AML check
    context_aml = InvestigationContext(
        investigation_id="INV-K-AML",
        transaction_id="TX-K-AML",
        transaction_data={"amount": 50000.0, "currency": "USD", "category": "aml"},
        prediction_result={"prediction": "High Risk", "probability": 0.99},
        fraud_probability=0.99,
        risk_score=10,
        priority="HIGH"
    )
    context_aml.add_evidence(
        agent_name="CustomerAgent",
        key_finding="Global sanctions name matches",
        details="Transactor on global watchlists."
    )
    
    res_aml = agent.execute(context_aml)
    assert res_aml.status == "SUCCESS"
    assert any("sanctions listings" in ev["description"] for ev in res_aml.evidence)
    assert any("sanctions list databases" in rec for rec in res_aml.recommendations)
    
    # 2. PCI card masking check
    context_pci = InvestigationContext(
        investigation_id="INV-K-PCI",
        transaction_id="TX-K-PCI",
        transaction_data={"amount": 15.0, "currency": "USD", "category": "pci"},
        prediction_result={"prediction": "Legitimate", "probability": 0.02},
        fraud_probability=0.02,
        risk_score=2,
        priority="LOW"
    )
    context_pci.add_evidence(
        agent_name="DeviceAgent",
        key_finding="Card display rules queries",
        details="Verify masking digits guidelines under PCI."
    )
    
    res_pci = agent.execute(context_pci)
    assert res_pci.status == "SUCCESS"
    assert any("mask all digits" in ev["description"] for ev in res_pci.evidence)
    assert any("account data masks" in rec for rec in res_pci.recommendations)

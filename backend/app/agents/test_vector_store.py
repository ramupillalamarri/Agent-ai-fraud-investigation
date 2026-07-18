import sys
import os
import pytest
from typing import List, Dict, Any

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.providers.chromadb_provider import ChromaDBProvider
from app.agents.investigators.knowledge.services.vector_store_service import VectorStoreService
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult

@pytest.fixture
def store_setup():
    config = KnowledgeAgentConfig(collection_name="test_collection_99")
    provider = ChromaDBProvider(config)
    service = VectorStoreService(provider)
    return config, provider, service

def test_vector_store_workflow(store_setup):
    """Verify standard CRUD and search operations in the vector store database layer."""
    config, provider, service = store_setup
    
    # 1. Health check verification
    assert provider.health_check() is True
    
    # 2. Insert mock document chunks
    chunks = [
        {
            "chunk_id": "chunk_doc1_0",
            "document_id": "doc1",
            "content": "SOP states customer signature satisfies chargeback validation.",
            "embedding": [0.1, 0.9, 0.0],
            "category": "compliance",
            "source": "compliance_playbook.md",
            "section_title": "Chargebacks",
            "page_number": 2
        },
        {
            "chunk_id": "chunk_doc2_0",
            "document_id": "doc2",
            "content": "AML regulations enforce identifying users transacting over $1000.",
            "embedding": [0.0, 0.1, 0.9],
            "category": "aml",
            "source": "aml_guidelines.txt",
            "section_title": "Transactions",
            "page_number": 5
        }
    ]
    
    service.index_chunks(chunks)
    
    # Verify count metrics
    stats = provider.get_statistics()
    assert stats["count"] == 2
    
    # 3. Similarity search query matching aml
    q_vec_aml = [0.0, 0.15, 0.85]
    results_aml = service.search(q_vec_aml, top_k=1, category_filter="aml")
    assert len(results_aml) == 1
    assert results_aml[0].document_id == "doc2"
    assert "AML regulations" in results_aml[0].content
    
    # 4. Similarity search matching compliance
    q_vec_cb = [0.15, 0.85, 0.0]
    results_cb = service.search(q_vec_cb, top_k=1, category_filter="compliance")
    assert len(results_cb) == 1
    assert results_cb[0].document_id == "doc1"
    assert "signature satisfies" in results_cb[0].content

    # 5. Update vector metadata
    updated_chunks = [
        {
            "chunk_id": "chunk_doc1_0",
            "document_id": "doc1",
            "content": "SOP states customer signature is mandatory for validation.",
            "embedding": [0.1, 0.9, 0.0],
            "category": "compliance",
            "source": "compliance_playbook.md",
            "section_title": "Chargebacks",
            "page_number": 2,
            "document_version": "2.0.0"
        }
    ]
    service.index_chunks(updated_chunks)
    
    # Verify count stays 2 (deduplicated index)
    assert provider.get_statistics()["count"] == 2
    
    # Search again to verify content was updated
    res_updated = service.search(q_vec_cb, top_k=1, category_filter="compliance")
    assert "mandatory for validation" in res_updated[0].content
    assert res_updated[0].metadata["document_version"] == "2.0.0"

    # 6. Delete document
    service.delete_document("doc2")
    assert provider.get_statistics()["count"] == 1
    
    # Verify aml chunk is gone
    empty_results = service.search(q_vec_aml, top_k=1, category_filter="aml")
    assert len(empty_results) == 0

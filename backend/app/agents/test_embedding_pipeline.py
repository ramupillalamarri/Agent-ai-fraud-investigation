import sys
import os
import pytest
from typing import List, Dict, Any

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.models.knowledge_document import KnowledgeDocument
from app.agents.investigators.knowledge.providers.embedding_provider import EmbeddingProvider
from app.agents.investigators.knowledge.services.embedding_service import EmbeddingService

# 1. Define mock embedding provider
class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self.call_count = 0

    def embed_query(self, text: str) -> List[float]:
        self.call_count += 1
        return [0.1, 0.2, 0.3]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        self.call_count += len(texts)
        return [[0.1, 0.2, 0.3] for _ in texts]

@pytest.fixture
def test_setup():
    config = KnowledgeAgentConfig(chunk_size=100, chunk_overlap=10)
    provider = MockEmbeddingProvider()
    service = EmbeddingService(config, provider)
    return config, provider, service

def test_short_document(test_setup):
    """Verify that a short document fits into a single chunk."""
    config, provider, service = test_setup
    
    doc = KnowledgeDocument(
        document_id="doc_short",
        title="Short SOP",
        source="internal",
        category="compliance",
        content="Clean playbooks contain active standards.",
        metadata={"sha256_hash": "hash_short"}
    )
    
    chunks = service.embed_document(doc, strategy="fixed")
    
    assert len(chunks) == 1
    assert chunks[0]["content"] == "Clean playbooks contain active standards."
    assert "embedding" in chunks[0]
    assert provider.call_count == 1

def test_large_document(test_setup):
    """Verify that a larger document gets split into multiple chunks with correct metadata."""
    config, provider, service = test_setup
    
    # 250 characters should trigger multiple chunks when chunk_size=100
    large_content = (
        "This is paragraph one of the compliance playbook. It specifies basic OFAC rules. "
        "This is paragraph two. It specifies chargeback guidelines. "
        "This is paragraph three. It outlines AML customer identification requirements."
    )
    
    doc = KnowledgeDocument(
        document_id="doc_large",
        title="Large SOP",
        source="internal",
        category="compliance",
        content=large_content,
        metadata={"sha256_hash": "hash_large"}
    )
    
    chunks = service.embed_document(doc, strategy="fixed")
    
    assert len(chunks) > 1
    for c in chunks:
        assert "embedding" in c
        assert c["token_count"] > 0
        assert c["start_offset"] < c["end_offset"]
        assert c["section_title"] == "Introduction"

def test_cache_hit_and_miss(test_setup):
    """Verify that second requests query the local cache and bypass embedding generation."""
    config, provider, service = test_setup
    
    doc = KnowledgeDocument(
        document_id="doc_cache_test",
        title="Cache test doc",
        source="internal",
        category="compliance",
        content="This statement will be cached.",
        metadata={"sha256_hash": "hash_unique_1001"}
    )
    
    # 1st run: Cache Miss -> calls provider
    chunks1 = service.embed_document(doc, strategy="fixed")
    assert provider.call_count == 1
    
    # 2nd run: Cache Hit -> skips provider
    chunks2 = service.embed_document(doc, strategy="fixed")
    assert provider.call_count == 1  # count stays at 1
    assert chunks1 == chunks2

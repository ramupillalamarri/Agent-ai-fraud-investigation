import time
import logging
from typing import List, Dict, Any, Optional
from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.document_loader import DocumentLoader
from app.agents.investigators.knowledge.vector_store import LocalVectorStore

logger = logging.getLogger("app.agents.KnowledgeAgent.Retriever")

class KnowledgeRetriever:
    """Manages document retrieval, executing similarity searches and recording latency performance."""

    def __init__(self, config: KnowledgeAgentConfig) -> None:
        self.config = config
        self.loader = DocumentLoader(self.config)
        self.vector_store = LocalVectorStore(self.config)
        self._initialized = False

    def initialize(self) -> None:
        """Loads and indexes playbooks into the vector database."""
        if self._initialized:
            return
        docs = self.loader.load_all()
        self.vector_store.index_documents(docs)
        self._initialized = True

    def retrieve(
        self, 
        query: str, 
        top_k: Optional[int] = None, 
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Performs semantic query lookup over playbooks, compiling retrieved passages and metadata."""
        start_time = time.perf_counter()
        
        self.initialize()
        
        limit = top_k or self.config.top_k
        matches = self.vector_store.similarity_search(
            query=query, 
            top_k=limit, 
            filter_metadata=filter_metadata
        )
        
        passages = []
        for doc, score in matches:
            if score >= self.config.similarity_threshold:
                passages.append({
                    "content": doc.page_content,
                    "score": score,
                    "metadata": doc.metadata
                })
                
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        
        return {
            "query": query,
            "passages": passages,
            "latency_ms": latency_ms,
            "confidence_score": sum(p["score"] for p in passages) / len(passages) if passages else 0.0
        }

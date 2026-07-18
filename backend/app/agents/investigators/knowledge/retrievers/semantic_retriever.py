import logging
from typing import List
from app.agents.investigators.knowledge.retrievers.base_retriever import BaseRetriever
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult
from app.agents.investigators.knowledge.providers.embedding_provider import EmbeddingProvider
from app.agents.investigators.knowledge.providers.vector_store_provider import VectorStoreProvider

logger = logging.getLogger("app.agents.investigators.knowledge.retrievers.semantic_retriever")

class SemanticRetriever(BaseRetriever):
    """Retrieves document chunks using vector embedding similarity matching."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store_provider: VectorStoreProvider,
        similarity_threshold: float = 0.50
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store_provider = vector_store_provider
        self.similarity_threshold = similarity_threshold

    def retrieve(self, query: str, top_k: int) -> List[RetrievalResult]:
        """Runs query embedding and executes similarity search filtering results by threshold."""
        logger.info("Executing semantic search for query: '%s'", query)
        
        query_vector = self.embedding_provider.embed_query(query)
        raw_results = self.vector_store_provider.similarity_search(query_vector, top_k)
        
        # Filter by similarity threshold
        filtered_results = [
            r for r in raw_results
            if r.score >= self.similarity_threshold
        ]
        
        logger.info(
            "Semantic search completed: retrieved %d chunks (filtered from %d)",
            len(filtered_results), len(raw_results)
        )
        return filtered_results
export_retriever = SemanticRetriever

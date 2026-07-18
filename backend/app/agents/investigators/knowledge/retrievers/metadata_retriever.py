import logging
from typing import List, Dict, Any, Optional
from app.agents.investigators.knowledge.retrievers.base_retriever import BaseRetriever
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult
from app.agents.investigators.knowledge.providers.vector_store_provider import VectorStoreProvider
from app.agents.investigators.knowledge.providers.embedding_provider import EmbeddingProvider

logger = logging.getLogger("app.agents.investigators.knowledge.retrievers.metadata_retriever")

class MetadataRetriever(BaseRetriever):
    """Retrieves document chunks using metadata filters combined with query similarity search."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store_provider: VectorStoreProvider,
        default_filter: Optional[Dict[str, Any]] = None
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store_provider = vector_store_provider
        self.default_filter = default_filter or {}

    def retrieve(self, query: str, top_k: int) -> List[RetrievalResult]:
        """Runs retrieval utilizing the default filter settings."""
        return self.retrieve_filtered(query, top_k, self.default_filter)

    def retrieve_filtered(self, query: str, top_k: int, metadata_filter: Dict[str, Any]) -> List[RetrievalResult]:
        """Runs vector search while enforcing metadata dictionary filters (category, version, etc.)."""
        logger.info("Executing metadata-filtered search. Filters: %s", metadata_filter)
        
        query_vector = self.embedding_provider.embed_query(query)
        
        search_filter_method = getattr(self.vector_store_provider, "similarity_search_with_filter", None)
        if search_filter_method:
            results = search_filter_method(query_vector, top_k, metadata_filter)
        else:
            # Fallback
            results = self.vector_store_provider.similarity_search(query_vector, top_k)
            
        logger.info("Metadata-filtered search completed: retrieved %d chunks", len(results))
        return results
export_retriever = MetadataRetriever

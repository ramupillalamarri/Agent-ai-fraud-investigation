from typing import List
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult
from app.agents.investigators.knowledge.retrievers.base_retriever import BaseRetriever
from app.agents.investigators.knowledge.providers.embedding_provider import EmbeddingProvider
from app.agents.investigators.knowledge.providers.vector_store_provider import VectorStoreProvider

class ChunkRetriever(BaseRetriever):
    """Retrieves document chunks using vector similarity searches."""

    def __init__(self, embedding_provider: EmbeddingProvider, vector_store_provider: VectorStoreProvider) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store_provider = vector_store_provider

    def retrieve(self, query: str, top_k: int) -> List[RetrievalResult]:
        """Runs embedding generation on query and queries the similarity database."""
        # Skeleton implementation
        query_vector = self.embedding_provider.embed_query(query)
        return self.vector_store_provider.similarity_search(query_vector, top_k)

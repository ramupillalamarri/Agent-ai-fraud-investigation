from typing import List
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult
from app.agents.investigators.knowledge.retrievers.base_retriever import BaseRetriever
from app.agents.investigators.knowledge.retrievers.chunk_retriever import ChunkRetriever

class HybridRetriever(BaseRetriever):
    """Combines vector similarity and keyword search results to perform hybrid retrieval."""

    def __init__(self, chunk_retriever: ChunkRetriever) -> None:
        self.chunk_retriever = chunk_retriever

    def retrieve(self, query: str, top_k: int) -> List[RetrievalResult]:
        """Orchestrates combined keyword and vector retrieval steps."""
        # Skeleton implementation: calls vector search and would combine with keyword searches
        return self.chunk_retriever.retrieve(query, top_k)

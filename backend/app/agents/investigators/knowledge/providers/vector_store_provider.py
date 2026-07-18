from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult

class VectorStoreProvider(ABC):
    """Abstract interface representing a vector storage database (e.g. Chroma, Qdrant)."""

    @abstractmethod
    def add_vectors(self, ids: List[str], vectors: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """Upserts a list of document vectors with metadata into the database."""
        pass

    @abstractmethod
    def similarity_search(self, query_vector: List[float], top_k: int) -> List[RetrievalResult]:
        """Queries the vector database for the top_k most similar document chunks."""
        pass

from abc import ABC, abstractmethod
from typing import List
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult

class BaseRetriever(ABC):
    """Abstract interface representing a retriever component inside the RAG pipeline."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> List[RetrievalResult]:
        """Performs retrieval from the database based on a raw query string."""
        pass

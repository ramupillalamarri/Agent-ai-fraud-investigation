from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    """Abstract interface representing an embedding generation service."""

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Generates a vector embedding for a query string."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates vector embeddings for a list of document strings."""
        pass

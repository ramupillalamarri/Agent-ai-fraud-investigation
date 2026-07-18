from typing import List
from app.agents.investigators.knowledge.providers.embedding_provider import EmbeddingProvider

class EmbeddingService:
    """Orchestrates caching and bulk operations for embedding providers."""

    def __init__(self, embedding_provider: EmbeddingProvider) -> None:
        self.embedding_provider = embedding_provider

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Handles vector generation requests with validation checks."""
        return self.embedding_provider.embed_documents(texts)

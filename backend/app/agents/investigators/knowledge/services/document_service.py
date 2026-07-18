from typing import List
from app.agents.investigators.knowledge.models.knowledge_document import KnowledgeDocument
from app.agents.investigators.knowledge.providers.vector_store_provider import VectorStoreProvider
from app.agents.investigators.knowledge.providers.embedding_provider import EmbeddingProvider

class DocumentService:
    """Manages parsing, chunking, and index uploads of knowledge documents."""

    def __init__(self, vector_store_provider: VectorStoreProvider, embedding_provider: EmbeddingProvider) -> None:
        self.vector_store_provider = vector_store_provider
        self.embedding_provider = embedding_provider

    def ingest_document(self, doc: KnowledgeDocument) -> None:
        """Splits document content into chunks, embeds them, and uploads to vector store."""
        pass

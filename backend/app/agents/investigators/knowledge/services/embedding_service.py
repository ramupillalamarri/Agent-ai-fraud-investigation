import logging
from typing import Dict, Any, List, Optional
from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.models.knowledge_document import KnowledgeDocument
from app.agents.investigators.knowledge.providers.embedding_provider import EmbeddingProvider
from app.agents.investigators.knowledge.utils.chunker import DocumentChunker
from app.agents.investigators.knowledge.utils.token_counter import TokenCounter
from app.agents.investigators.knowledge.utils.embedding_cache import EmbeddingCache

logger = logging.getLogger("app.agents.investigators.knowledge.services.embedding_service")

class EmbeddingService:
    """ETL Service coordinating document chunking, token counts, cache verification, and vector generation."""

    def __init__(
        self,
        config: KnowledgeAgentConfig,
        embedding_provider: EmbeddingProvider,
        chunker: Optional[DocumentChunker] = None,
        token_counter: Optional[TokenCounter] = None,
        cache: Optional[EmbeddingCache] = None
    ) -> None:
        self.config = config
        self.embedding_provider = embedding_provider
        self.chunker = chunker or DocumentChunker(config)
        self.token_counter = token_counter or TokenCounter(config.embedding_model)
        self.cache = cache or EmbeddingCache(config.cache_enabled)

    def embed_document(self, doc: KnowledgeDocument, strategy: str = "recursive") -> List[Dict[str, Any]]:
        """Processes a KnowledgeDocument, chunking text, counting tokens, querying cache, and generating vector embeddings."""
        doc_hash = doc.metadata.get("sha256_hash", "")
        
        # 1. Cache hit verification
        if doc_hash:
            cached_chunks = self.cache.get(doc_hash)
            if cached_chunks is not None:
                logger.info("Cache hits for document: %s", doc.document_id)
                return cached_chunks
            logger.info("Cache misses for document: %s", doc.document_id)

        # 2. Chunking phase
        logger.info("Chunking started for document: %s", doc.document_id)
        chunks = self.chunker.split_document(doc.content, doc.document_id, strategy=strategy)
        logger.info("Chunking completed: split into %d chunks", len(chunks))

        if not chunks:
            return []

        # 3. Token count telemetry
        stats = self.token_counter.calculate_statistics(chunks, doc.content)
        logger.info(
            "Token counts: total document=%d, avg chunk=%.1f, max chunk=%d",
            stats["document_tokens"], stats["average_chunk_size_tokens"], stats["maximum_chunk_size_tokens"]
        )

        # 4. Vector generation phase
        logger.info("Embedding generation started for %d chunks", len(chunks))
        texts = [c["content"] for c in chunks]
        embeddings = self.embedding_provider.embed_documents(texts)
        
        for idx, chunk in enumerate(chunks):
            # Inject embedding array into chunk payload
            chunk["embedding"] = embeddings[idx]

        logger.info("Embedding generation completed")

        # 5. Cache registry updates
        if doc_hash:
            self.cache.set(doc_hash, chunks)

        return chunks

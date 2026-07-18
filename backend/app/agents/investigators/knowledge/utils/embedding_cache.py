import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("app.agents.investigators.knowledge.utils.embedding_cache")

class EmbeddingCache:
    """Session cache registry storing calculated document chunk vectors to bypass redundant generation queries."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self._store: Dict[str, List[Dict[str, Any]]] = {}

    def get(self, doc_hash: str) -> Optional[List[Dict[str, Any]]]:
        """Queries the cache registry for precalculated document chunks."""
        if not self.enabled:
            return None
            
        result = self._store.get(doc_hash)
        if result:
            logger.info("Cache hit for document hash: %s", doc_hash)
            return result
            
        logger.info("Cache miss for document hash: %s", doc_hash)
        return None

    def set(self, doc_hash: str, embedded_chunks: List[Dict[str, Any]]) -> None:
        """Stores calculated embedded chunks keyed on document hash."""
        if not self.enabled:
            return
        self._store[doc_hash] = embedded_chunks
        logger.info("Cache updated for document hash: %s", doc_hash)

    def clear(self) -> None:
        """Clears all entries inside cache."""
        self._store.clear()
export_embedding_cache = EmbeddingCache

import logging
from typing import List, Dict, Any, Optional
from app.agents.investigators.knowledge.retrievers.base_retriever import BaseRetriever
from app.agents.investigators.knowledge.retrievers.semantic_retriever import SemanticRetriever
from app.agents.investigators.knowledge.retrievers.metadata_retriever import MetadataRetriever
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult

logger = logging.getLogger("app.agents.investigators.knowledge.retrievers.hybrid_retriever")

class HybridRetriever(BaseRetriever):
    """Combines semantic search vectors, metadata filters, and content keyword indexing to perform hybrid search retrieval."""

    def __init__(
        self,
        semantic_retriever: SemanticRetriever,
        metadata_retriever: MetadataRetriever,
        enable_keyword_matching: bool = True
    ) -> None:
        self.semantic_retriever = semantic_retriever
        self.metadata_retriever = metadata_retriever
        self.enable_keyword_matching = enable_keyword_matching

    def retrieve(self, query: str, top_k: int) -> List[RetrievalResult]:
        """Runs hybrid search retrieval combining vector similarity scores and text keyword indicators."""
        return self.retrieve_hybrid(query, top_k, None)

    def retrieve_hybrid(self, query: str, top_k: int, metadata_filter: Optional[Dict[str, Any]]) -> List[RetrievalResult]:
        """Performs retrieval combining semantic searches, metadata bounds, and text string matches."""
        logger.info("Executing hybrid search for query: '%s'", query)

        # 1. Gather semantic search chunks
        semantic_chunks = self.semantic_retriever.retrieve(query, top_k * 2)

        # 2. Gather metadata-filtered chunks if filter exists
        filtered_chunks = []
        if metadata_filter:
            filtered_chunks = self.metadata_retriever.retrieve_filtered(query, top_k * 2, metadata_filter)

        # Combine unique chunks by chunk ID
        combined_dict = {}
        for chunk in semantic_chunks + filtered_chunks:
            combined_dict[chunk.chunk_id] = chunk

        # 3. Apply keyword search matches (BM25-style frequency counting fallback)
        query_words = set(w.lower().strip() for w in query.split() if len(w) > 2)
        
        chunk_list = list(combined_dict.values())
        for chunk in chunk_list:
            if self.enable_keyword_matching and query_words:
                content_lower = chunk.content.lower()
                # Count matching query terms
                matches = sum(1 for w in query_words if w in content_lower)
                keyword_score = matches / len(query_words)
                # Weighted blend: 70% semantic similarity + 30% keyword match density
                chunk.score = (chunk.score * 0.7) + (keyword_score * 0.3)

        # Sort and return top_k
        chunk_list.sort(key=lambda x: x.score, reverse=True)
        results = chunk_list[:top_k]
        
        logger.info("Hybrid search completed: returned %d blended chunks", len(results))
        return results
export_retriever = HybridRetriever

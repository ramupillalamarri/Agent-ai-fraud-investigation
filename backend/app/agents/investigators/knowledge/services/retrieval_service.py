import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.models.retrieved_context import RetrievedContext
from app.agents.investigators.knowledge.retrievers.hybrid_retriever import HybridRetriever
from app.agents.investigators.knowledge.providers.llm_provider import LLMProvider
from app.agents.investigators.knowledge.utils.query_builder import QueryBuilder
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult

logger = logging.getLogger("app.agents.investigators.knowledge.services.retrieval_service")

class RelevanceScoringStrategy:
    """Calculates weighted similarity scores combining cosine, metadata matches, and document recency."""

    def __init__(self, config: KnowledgeAgentConfig) -> None:
        self.config = config

    def score_chunk(self, chunk: RetrievalResult) -> float:
        """Computes final score adding configured metadata boosts and recency weights."""
        base_score = chunk.score
        
        # 1. Metadata boost
        meta = chunk.metadata or {}
        category_boost = 0.0
        # If document matches prioritized retail fraud guidelines
        if meta.get("category") in ["fraud_playbooks", "compliance"]:
            category_boost = self.config.metadata_boost
            
        # 2. Recency score decay
        recency_score = 0.0
        created_str = meta.get("created_at", "") or meta.get("created_date", "")
        if created_str:
            try:
                # Basic age factor calculations
                created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                days_old = (datetime.utcnow() - created_dt.replace(tzinfo=None)).days
                # Decays score based on document age (newer files receive higher values)
                recency_score = 1.0 / (1.0 + (days_old / 365.0))
            except Exception:
                recency_score = 0.5  # default/neutral weight

        final_score = base_score + category_boost + (recency_score * self.config.recency_weight)
        
        # Cap score between 0.0 and 1.0
        return min(max(final_score, 0.0), 1.0)


class RetrievalService:
    """Orchestrates multi-query retrieval, relevance scoring strategies, and result synthesis."""

    def __init__(
        self,
        config: KnowledgeAgentConfig,
        hybrid_retriever: HybridRetriever,
        llm_provider: Optional[LLMProvider] = None,
        query_builder: Optional[QueryBuilder] = None,
        scoring_strategy: Optional[RelevanceScoringStrategy] = None
    ) -> None:
        self.config = config
        self.hybrid_retriever = hybrid_retriever
        self.llm_provider = llm_provider
        self.query_builder = query_builder or QueryBuilder()
        self.scoring_strategy = scoring_strategy or RelevanceScoringStrategy(config)

    def retrieve_context(self, query: str, top_k: int) -> RetrievedContext:
        """Performs RAG hybrid retrieval and constructs RetrievedContext."""
        return self.retrieve_context_filtered(query, top_k, None)

    def retrieve_context_filtered(self, query: str, top_k: int, category_filter: Optional[str] = None) -> RetrievedContext:
        """Retrieves and scores document chunks filtering by metadata categories."""
        start_time = time.perf_counter()
        logger.info("Retrieval Service started for query: '%s'", query)

        # 1. Run hybrid retriever
        filter_dict = {"category": category_filter} if category_filter else None
        chunks = self.hybrid_retriever.retrieve_hybrid(query, top_k * 2, filter_dict)

        # 2. Score and rerank chunks using RelevanceScoringStrategy
        scored_chunks = []
        for chunk in chunks:
            chunk.score = self.scoring_strategy.score_chunk(chunk)
            scored_chunks.append(chunk)

        # Re-sort after strategy scoring
        scored_chunks.sort(key=lambda x: x.score, reverse=True)
        final_chunks = scored_chunks[:top_k]

        # 3. Extract unique source filepaths
        sources = list(set(c.metadata.get("source", "unknown") for c in final_chunks))

        # 4. Calculate aggregated confidence score
        confidence = sum(c.score for c in final_chunks) / len(final_chunks) if final_chunks else 1.0

        latency = (time.perf_counter() - start_time) * 1000.0
        logger.info("Retrieval Service completed in %.2fms", latency)

        return RetrievedContext(
            query=query,
            retrieved_chunks=final_chunks,
            sources=sources,
            confidence=round(confidence, 2),
            latency_ms=latency
        )

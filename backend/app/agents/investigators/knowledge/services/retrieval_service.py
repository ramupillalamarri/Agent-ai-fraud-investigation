import time
from app.agents.investigators.knowledge.models.retrieved_context import RetrievedContext
from app.agents.investigators.knowledge.retrievers.base_retriever import BaseRetriever
from app.agents.investigators.knowledge.providers.llm_provider import LLMProvider

class RetrievalService:
    """Coordinates retrieval pipeline steps, ranking operations, and retrieved context construction."""

    def __init__(self, retriever: BaseRetriever, llm_provider: LLMProvider) -> None:
        self.retriever = retriever
        self.llm_provider = llm_provider

    def retrieve_context(self, query: str, top_k: int) -> RetrievedContext:
        """Runs RAG retrieval pipeline and returns unified context model payload."""
        start_time = time.perf_counter()
        chunks = self.retriever.retrieve(query, top_k)
        sources = list(set(c.document_id for c in chunks))
        latency = (time.perf_counter() - start_time) * 1000.0
        
        return RetrievedContext(
            query=query,
            retrieved_chunks=chunks,
            sources=sources,
            confidence=0.90 if chunks else 1.0,
            latency_ms=latency
        )

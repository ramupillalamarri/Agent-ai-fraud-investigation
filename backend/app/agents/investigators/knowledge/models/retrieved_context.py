from typing import List
from pydantic import BaseModel, Field
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult

class RetrievedContext(BaseModel):
    """Data contract representing the aggregated context returned by the retrieval pipeline."""
    query: str
    retrieved_chunks: List[RetrievalResult] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    confidence: float
    latency_ms: float

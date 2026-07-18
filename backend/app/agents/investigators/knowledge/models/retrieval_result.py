from typing import Dict, Any
from pydantic import BaseModel, Field

class RetrievalResult(BaseModel):
    """Data contract representing a single retrieved text chunk from the knowledge base."""
    document_id: str
    chunk_id: str
    score: float
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

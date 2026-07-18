from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class KnowledgeDocument(BaseModel):
    """Data contract representing a single indexed document in the knowledge base."""
    document_id: str
    title: str
    source: str
    category: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

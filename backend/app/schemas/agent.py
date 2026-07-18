from typing import List, Optional
from pydantic import BaseModel, Field

class AgentResponse(BaseModel):
    """Schema representing the details of an AI investigation agent."""
    id: str
    name: str
    description: str
    version: str
    priority: int
    enabled: bool
    type: str
    health_status: bool

class AgentUpdate(BaseModel):
    """Schema for updating agent configurations."""
    enabled: Optional[bool] = None
    priority: Optional[int] = None
    execution_priority: Optional[int] = None

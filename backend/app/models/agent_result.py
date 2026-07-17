import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy import String, Float, Integer, ForeignKey, UUID, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDModelMixin, TimeStampedModelMixin

class AgentResult(Base, UUIDModelMixin, TimeStampedModelMixin):
    """Represents execution parameters and outputs of an individual investigation agent."""
    __tablename__ = "agent_results"

    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("investigations.id", ondelete="CASCADE"), 
        nullable=False
    )
    agent_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    additional_metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False)

    # Relationships
    investigation: Mapped["Investigation"] = relationship(
        "Investigation", 
        back_populates="agent_results"
    )
    evidence: Mapped[List["Evidence"]] = relationship(
        "Evidence", 
        back_populates="agent_result", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

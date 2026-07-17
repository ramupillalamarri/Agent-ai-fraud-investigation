import uuid
from typing import Dict, Any, Optional
from sqlalchemy import String, Float, ForeignKey, Text, UUID, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDModelMixin, TimeStampedModelMixin

class Evidence(Base, UUIDModelMixin, TimeStampedModelMixin):
    """Represents a structured piece of verified transaction audit evidence gathered by agents."""
    __tablename__ = "evidence"

    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("investigations.id", ondelete="CASCADE"), 
        nullable=False
    )
    agent_result_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("agent_results.id", ondelete="CASCADE"), 
        nullable=True
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    additional_metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False)

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="evidence")
    agent_result: Mapped[Optional["AgentResult"]] = relationship("AgentResult", back_populates="evidence")

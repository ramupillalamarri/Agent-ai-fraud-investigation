import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy import String, ForeignKey, Text, DateTime, UUID, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDModelMixin

class InvestigationTimeline(Base, UUIDModelMixin):
    """Represents audit trail lifecycle events occurred during the transaction investigation workflow."""
    __tablename__ = "investigation_timelines"

    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("investigations.id", ondelete="CASCADE"), 
        nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_description: Mapped[str] = mapped_column(Text, nullable=False)
    agent_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        index=True, 
        nullable=False
    )
    additional_metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False)

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="timeline")

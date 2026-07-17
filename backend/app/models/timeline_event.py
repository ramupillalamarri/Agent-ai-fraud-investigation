import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy import String, ForeignKey, Text, DateTime, UUID, JSON, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDModelMixin

class TimelineEvent(Base, UUIDModelMixin):
    """Represents audit trail lifecycle events occurred during the transaction investigation workflow."""
    __tablename__ = "investigation_timelines"

    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("investigations.id", ondelete="CASCADE"), 
        index=True,
        nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column("event_description", Text, nullable=False)
    agent_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        index=True, 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        index=True, 
        nullable=False
    )
    additional_metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False)

    @property
    def event_description(self) -> str:
        """Alias property for backward compatibility with the event_description column."""
        return self.description

    @event_description.setter
    def event_description(self, value: str) -> None:
        self.description = value

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="timeline")

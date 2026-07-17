import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, UUID, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDModelMixin, TimeStampedModelMixin

class Investigation(Base, UUIDModelMixin, TimeStampedModelMixin):
    """Represents a retail fraud audit investigation dossier in PostgreSQL."""
    __tablename__ = "investigations"

    transaction_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="LOW", index=True, nullable=False)
    fraud_probability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overall_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    additional_metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict, nullable=False)

    # Relationships
    agent_results: Mapped[List["AgentResult"]] = relationship(
        "AgentResult", 
        back_populates="investigation", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    evidence: Mapped[List["Evidence"]] = relationship(
        "Evidence", 
        back_populates="investigation", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation", 
        back_populates="investigation", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    timeline: Mapped[List["InvestigationTimeline"]] = relationship(
        "InvestigationTimeline", 
        back_populates="investigation", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

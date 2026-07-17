import uuid
import random
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, UUID, JSON, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDModelMixin, TimeStampedModelMixin

def generate_case_number() -> str:
    """Generates a human-readable unique case number, e.g. INV-2026-000123."""
    year = datetime.now(timezone.utc).year
    rand_seq = random.randint(100000, 999999)
    return f"INV-{year}-{rand_seq:06d}"

class Investigation(Base, UUIDModelMixin, TimeStampedModelMixin):
    """Represents a retail fraud audit investigation dossier in PostgreSQL."""
    __tablename__ = "investigations"

    transaction_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    case_number: Mapped[str] = mapped_column(
        String(100), 
        default=generate_case_number,
        unique=True, 
        index=True, 
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="LOW", index=True, nullable=False)
    fraud_probability: Mapped[float] = mapped_column(Float, default=0.0, index=True, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    overall_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    prediction: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )
    
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
    )
    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(
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
    timeline: Mapped[List["TimelineEvent"]] = relationship(
        "TimelineEvent", 
        back_populates="investigation", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

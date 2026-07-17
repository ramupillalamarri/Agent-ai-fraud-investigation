import uuid
from sqlalchemy import String, ForeignKey, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDModelMixin, TimeStampedModelMixin

class Recommendation(Base, UUIDModelMixin, TimeStampedModelMixin):
    """Represents an actionable mitigation/risk treatment proposal for a flagged transaction."""
    __tablename__ = "recommendations"

    investigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("investigations.id", ondelete="CASCADE"), 
        nullable=False
    )
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False)
    generated_by: Mapped[str] = mapped_column(String(255), nullable=False)  # Agent or Operator name
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # e.g., PENDING, APPLIED, DISMISSED

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="recommendations")

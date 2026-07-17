import uuid
from typing import Optional
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
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column("recommendation", Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False)
    generated_by: Mapped[str] = mapped_column(String(255), nullable=False)  # Agent or Operator name
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # e.g., PENDING, APPLIED, DISMISSED

    @property
    def recommendation(self) -> str:
        """Alias property for backward compatibility with the recommendation column."""
        return self.description

    @recommendation.setter
    def recommendation(self, value: str) -> None:
        self.description = value

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="recommendations")

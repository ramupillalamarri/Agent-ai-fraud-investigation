from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import (
    Base,
    UUIDModelMixin,
    TimeStampedModelMixin,
    SoftDeleteModelMixin,
)

if TYPE_CHECKING:
    from app.models.role import Role


class Permission(Base, UUIDModelMixin, TimeStampedModelMixin, SoftDeleteModelMixin):
    """SQLAlchemy model representing a granular authorization permission scope."""

    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
    )

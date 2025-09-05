"""Domain entity representing a user session."""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentra.domain.entities.base_entity import BaseEntity


class SessionEntity(BaseEntity):
    """Persisted session metadata."""

    # NOTE: Underlying table still named "conversations" until migration runs
    __tablename__ = "sessions"

    title: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    initial_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    created_by_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("UserEntity", back_populates="sessions")

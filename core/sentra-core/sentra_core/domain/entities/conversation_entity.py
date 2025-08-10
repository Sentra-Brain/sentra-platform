# services/sentra-core/sentra_core/domain/conversation_entity.py
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sentra_core.domain.entities.base_entity import BaseEntity

class ConversationEntity(BaseEntity):
    __tablename__ = "conversations"

    title: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    created_by_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("UserEntity", back_populates="conversations")

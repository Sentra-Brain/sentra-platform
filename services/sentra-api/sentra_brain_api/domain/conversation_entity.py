# sentra_brain_api/domain/conversation_entity.py
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sentra_brain_api.domain.base_entity import BaseEntity

class ConversationEntity(BaseEntity):
    __tablename__ = "conversations"

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    initial_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("UserEntity", back_populates="conversations")

# sentra_core/domain/entities/chat_settings.py

from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from sentra_core.domain.entities.base_entity import BaseEntity


class ChatSettingsEntity(BaseEntity):
    __tablename__ = "chat_settings"

    max_tokens: Mapped[int] = mapped_column(Integer, default=2048)
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    top_p: Mapped[float] = mapped_column(Float, default=0.9)
    top_k: Mapped[int] = mapped_column(Integer, default=40)
    system_prompt: Mapped[str] = mapped_column(String, default="Responde siempre en español.")
    stop_sequences: Mapped[str] = mapped_column(String, default=",User:,Assistant:")
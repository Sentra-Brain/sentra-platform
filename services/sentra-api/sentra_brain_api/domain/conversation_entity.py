# sentra_brain_api/domain/conversation_entity.py
from sqlalchemy import Column, String, DateTime, func
from sentra_brain_api.domain.base_entity import BaseEntity

class ConversationEntity(BaseEntity):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
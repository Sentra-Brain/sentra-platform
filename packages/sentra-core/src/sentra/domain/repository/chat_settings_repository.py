# sentra/domain/repository/chat_settings_repository.py

from sqlalchemy.orm import Session
from sentra.domain.repository.base_repository import BaseRepository
from sentra.domain.entities.chat_settings import ChatSettingsEntity


class ChatSettingsRepository(BaseRepository[ChatSettingsEntity]):
    def __init__(self, db: Session):
        super().__init__(ChatSettingsEntity, db)
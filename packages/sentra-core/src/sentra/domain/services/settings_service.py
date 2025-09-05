# sentra/domain/services/settings_service.py

from sqlalchemy.orm import Session
from sentra.domain.entities.system_settings import SystemSettingsEntity
from sentra.domain.entities.chat_settings import ChatSettingsEntity
from sentra.domain.repository.system_settings_repository import SystemSettingsRepository
from sentra.domain.repository.chat_settings_repository import ChatSettingsRepository


class SettingsService:
    def __init__(self, db: Session):
        self.system_repo = SystemSettingsRepository(db)
        self.chat_repo = ChatSettingsRepository(db)

    def get_system_settings(self) -> SystemSettingsEntity:
        return self.system_repo.db.query(SystemSettingsEntity).first()

    def update_system_settings(self, update: dict) -> SystemSettingsEntity:
        settings = self.get_system_settings()
        for field, value in update.items():
            setattr(settings, field, value)
        self.system_repo.update(settings)
        return settings

    def get_chat_settings(self) -> ChatSettingsEntity:
        return self.chat_repo.db.query(ChatSettingsEntity).first()

    def update_chat_settings(self, update: dict) -> ChatSettingsEntity:
        settings = self.get_chat_settings()
        for field, value in update.items():
            setattr(settings, field, value)
        self.chat_repo.update(settings)
        return settings
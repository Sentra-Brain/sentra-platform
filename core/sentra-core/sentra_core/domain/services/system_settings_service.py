# sentra_core/domain/services/system_settings_service.py

from sqlalchemy.orm import Session
from sentra_core.domain.entities.system_settings import SystemSettingsEntity
from sentra_core.domain.entities.user_entity import UserEntity

class SystemSettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_public_settings(self) -> tuple[str, int, int]:
        settings = self.db.query(SystemSettingsEntity).first()
        total_users = self.db.query(UserEntity).filter(~UserEntity.roles.contains("superadmin")).count()

        max_users = settings.max_users if settings else -1
        available = -1 if max_users == -1 else max(0, max_users - total_users)

        return settings.workspace_name, max_users, available

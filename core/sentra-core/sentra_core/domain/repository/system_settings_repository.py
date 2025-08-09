# sentra_core/domain/repository/system_settings_repository.py

from sqlalchemy.orm import Session
from sentra_core.domain.repository.base_repository import BaseRepository
from sentra_core.domain.entities.system_settings import SystemSettingsEntity


class SystemSettingsRepository(BaseRepository[SystemSettingsEntity]):
    def __init__(self, db: Session):
        super().__init__(SystemSettingsEntity, db)
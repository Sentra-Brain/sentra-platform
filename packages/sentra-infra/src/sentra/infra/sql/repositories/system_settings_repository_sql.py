# packages/sentra-infra/src/sentra/infra/sql/repositories/system_settings_repository_sql.py
from sqlalchemy.orm import Session
from sentra.domain.entities.system_settings import SystemSettingsEntity
from sentra.domain.repository.system_settings_repository import ISystemSettingsRepository
from sentra.infra.sql.repositories.base_repository import BaseRepository

class SystemSettingsRepositorySql(BaseRepository[SystemSettingsEntity], ISystemSettingsRepository):
    def __init__(self, db: Session):
        super().__init__(SystemSettingsEntity, db)

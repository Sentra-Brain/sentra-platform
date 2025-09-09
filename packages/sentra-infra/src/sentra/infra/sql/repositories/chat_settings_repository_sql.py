# packages/sentra-infra/src/sentra/infra/sql/repositories/chat_settings_repository_sql.py
from sqlalchemy.orm import Session
from sentra.domain.entities.chat_settings import ChatSettingsEntity
from sentra.domain.repository.chat_settings_repository import IChatSettingsRepository
from sentra.infra.sql.repositories.base_repository import BaseRepository

class ChatSettingsRepositorySql(BaseRepository[ChatSettingsEntity], IChatSettingsRepository):
    def __init__(self, db: Session):
        super().__init__(ChatSettingsEntity, db)

import uuid
from sentra.domain.entities.chat_settings import ChatSettingsEntity
from sentra.domain.entities.base_entity import BaseEntity

def test_chat_settings_id_and_inheritance():
    settings = ChatSettingsEntity(id=uuid.uuid4())
    assert isinstance(settings, BaseEntity)
    assert isinstance(settings.id, uuid.UUID)

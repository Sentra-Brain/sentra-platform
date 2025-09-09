import uuid
from sentra.domain.entities.system_settings import SystemSettingsEntity
from sentra.domain.entities.base_entity import BaseEntity

def test_system_settings_id_and_inheritance():
    settings = SystemSettingsEntity(id=uuid.uuid4())
    assert isinstance(settings, BaseEntity)
    assert isinstance(settings.id, uuid.UUID)

import uuid
from sentra.domain.entities.user_entity import UserEntity
from sentra.domain.entities.base_entity import BaseEntity

def test_user_entity_id_and_inheritance():
    user = UserEntity(id=uuid.uuid4(), username="UserName", email="test@example.com")
    assert isinstance(user, BaseEntity)
    assert isinstance(user.id, uuid.UUID)

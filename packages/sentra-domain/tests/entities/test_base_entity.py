import uuid
from sentra.domain.entities.base_entity import BaseEntity

def test_base_entity_id_and_type():
    class DummyEntity(BaseEntity):
        __tablename__ = "dummy_entity"
    
    
    entity = DummyEntity(id=uuid.uuid4())
    assert isinstance(entity, BaseEntity)
    assert isinstance(entity.id, uuid.UUID)

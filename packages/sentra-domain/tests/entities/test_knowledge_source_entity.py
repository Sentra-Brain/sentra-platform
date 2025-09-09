import uuid
from sentra.domain.entities.knowledge_source_entity import KnowledgeSourceEntity
from sentra.domain.entities.base_entity import BaseEntity

def test_knowledge_source_entity_id_and_inheritance():
    ks = KnowledgeSourceEntity(id=uuid.uuid4(), name="KS")
    assert isinstance(ks, BaseEntity)
    assert isinstance(ks.id, uuid.UUID)

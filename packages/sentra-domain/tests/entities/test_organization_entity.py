import uuid
from sentra.domain.entities.organization_entity import OrganizationEntity
from sentra.domain.entities.base_entity import BaseEntity

def test_organization_entity_id_and_inheritance():
    org = OrganizationEntity(id=uuid.uuid4(), name="Org")
    assert isinstance(org, BaseEntity)
    assert isinstance(org.id, uuid.UUID)

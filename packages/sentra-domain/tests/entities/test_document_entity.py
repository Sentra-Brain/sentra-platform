import uuid
from sentra.domain.entities.document_entity import DocumentEntity
from sentra.domain.entities.base_entity import BaseEntity

def test_document_entity_id_and_inheritance():
    doc = DocumentEntity(id=uuid.uuid4(), filename="FileName.extension", display_name="Display Name", description="Description")
    assert isinstance(doc, BaseEntity)
    assert isinstance(doc.id, uuid.UUID)
    assert doc.filename == "FileName.extension"
    assert doc.display_name == "Display Name"
    assert doc.description == "Description"

import uuid
from sentra.domain.entities.session_entity import SessionEntity
from sentra.domain.entities.base_entity import BaseEntity

def test_session_entity_id_and_inheritance():
    session = SessionEntity(id=uuid.uuid4(), created_by_id=uuid.uuid4(), title="Session Title", description="Session Description", initial_prompt="Initial Prompt")
    assert isinstance(session, BaseEntity)
    assert isinstance(session.id, uuid.UUID)
    assert session.title == "Session Title"
    assert session.description == "Session Description"
    assert session.initial_prompt == "Initial Prompt"
    assert isinstance(session.created_by_id, uuid.UUID)
    
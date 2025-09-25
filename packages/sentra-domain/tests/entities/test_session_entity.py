import uuid
from sentra.domain.entities.session_entity import ConversationEntity
from sentra.domain.entities.base_entity import BaseEntity

def test_session_entity_id_and_inheritance():
    conversation = ConversationEntity(id=uuid.uuid4(), created_by_id=uuid.uuid4(), title="Session Title", description="Session Description", initial_prompt="Initial Prompt")
    assert isinstance(conversation, BaseEntity)
    assert isinstance(conversation.id, uuid.UUID)
    assert conversation.title == "Session Title"
    assert conversation.description == "Session Description"
    assert conversation.initial_prompt == "Initial Prompt"
    assert isinstance(conversation.created_by_id, uuid.UUID)
    
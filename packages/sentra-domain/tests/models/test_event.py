import pytest
from uuid import UUID
from sentra.domain.models.event import SentraEvent, SentraEventContent, SentraEventContentPart

def test_sentra_event_uuid_roundtrip():
    event = SentraEvent(
        author="user",
        type="message_final",
        content=SentraEventContent(role="user", parts=[SentraEventContentPart(text="hello")]),
    )
    dumped = event.model_dump()
    loaded = SentraEvent(**dumped)
    assert isinstance(loaded.id, UUID)
    assert loaded.author == "user"
    assert loaded.content.parts[0].text == "hello"

def test_sentra_event_id_is_uuid():
    event = SentraEvent(author="user", type="message_final")
    assert isinstance(event.id, UUID)

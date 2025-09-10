# packages/sentra-domain/tests/models/test_event.py
import json
from uuid import UUID
from sentra.domain.models.event import SentraEvent, SentraEventContent, SentraEventContentPart, SentraEventType

def test_sentra_event_uuid_roundtrip():
    event = SentraEvent(
        author="user",
        type=SentraEventType.MESSAGE_FINAL,
        content=SentraEventContent(role="user", parts=[SentraEventContentPart(text="hello")]),
    )
    dumped = event.model_dump()
    loaded = SentraEvent(**dumped)
    assert isinstance(loaded.id, UUID)
    assert loaded.author == "user"
    assert loaded.content.parts[0].text == "hello"

def test_sentra_event_id_is_uuid():
    event = SentraEvent(author="user", type=SentraEventType.MESSAGE_FINAL)
    assert isinstance(event.id, UUID)

def test_uuid_and_timestamp_are_generated():
    e = SentraEvent(author="user", type=SentraEventType.MESSAGE_FINAL)
    assert isinstance(e.id, UUID)
    assert e.timestamp is not None


def test_user_message_helper():
    e = SentraEvent.user_message("hello")
    assert e.author == "user"
    assert e.type == SentraEventType.MESSAGE_FINAL
    assert e.content.parts[0].text == "hello"


def test_assistant_message_helper():
    e = SentraEvent.assistant_message("hi")
    assert e.author == "assistant"
    assert e.type == SentraEventType.MESSAGE_FINAL
    assert e.content.parts[0].text == "hi"


def test_system_message_helper():
    e = SentraEvent.system_message("sys", type=SentraEventType.MESSAGE_FINAL)
    assert e.author == "system"
    assert e.type == SentraEventType.MESSAGE_FINAL
    assert e.content.parts[0].text == "sys"


def test_error_helper_sets_status():
    e = SentraEvent.error("boom")
    assert e.author == "system"
    assert e.type == SentraEventType.ERROR
    assert e.status == "error"
    assert e.content.parts[0].text == "boom"


def test_model_dump_json_normalizes():
    e = SentraEvent.user_message("hello")
    data = json.loads(e.model_dump_json(exclude_none=True, by_alias=True))
    assert isinstance(data["id"], str)
    assert "T" in data["timestamp"]
    assert data["content"]["parts"][0]["text"] == "hello"


def test_is_final_response_true_for_message_final():
    e = SentraEvent.assistant_message("done")
    assert e.is_final_response() is True


def test_is_final_response_false_for_delta():
    e = SentraEvent(
        author="assistant",
        type=SentraEventType.MESSAGE_DELTA,
        content=SentraEventContent(role="assistant", parts=[SentraEventContentPart(text="chunk")])
    )
    assert e.is_final_response() is False

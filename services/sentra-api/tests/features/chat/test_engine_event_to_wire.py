from datetime import datetime, timezone
from uuid import uuid4

from sentra.schemas import Event
from sentra_brain_api.features.chat.mappers import event_to_wire


def test_message_final_delivers_content():
    final_text = "Hello world!"
    evt = Event(
        id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        type="message_final",
        role="assistant",
        content=final_text,
    )
    out = event_to_wire(evt)
    assert out.type == "message_final"
    assert out.content == final_text


def test_engine_event_generates_missing_fields():
    """Events lacking identifiers should be populated automatically."""
    evt = Event(type="message_final", role="assistant", content="hi")
    out = event_to_wire(evt)
    # Event should now have id/timestamp set
    assert evt.id is not None
    assert evt.timestamp is not None
    # And the wire model should reflect those values
    assert out.id == evt.id
    assert out.timestamp == evt.timestamp

from datetime import datetime, timezone
from uuid import uuid4

from sentra.domain.models.event import SentraEvent
from sentra_brain_api.features.chat.mappers import engine_event_to_wire


def test_message_final_delivers_content():
    final_text = "Hello world!"
    evt = SentraEvent(
        event_id=uuid4().hex,
        timestamp=datetime.now(timezone.utc),
        type="message_final",
        author="assistant",
        content=final_text,
    )
    out = engine_event_to_wire(evt)
    assert out.type == "message_final"
    assert out.content == final_text


def test_engine_event_generates_missing_fields():
    """Events lacking identifiers should be populated automatically."""
    evt = SentraEvent(type="message_final", author="assistant", content="hi")
    out = engine_event_to_wire(evt)
    # SentraEvent should now have id/timestamp set
    assert evt.event_id is not None
    assert evt.timestamp is not None
    # And the wire model should reflect those values
    assert out.event_id == evt.event_id
    assert out.timestamp == evt.timestamp.isoformat()

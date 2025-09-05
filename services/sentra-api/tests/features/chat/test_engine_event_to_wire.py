from datetime import datetime, timezone
from uuid import uuid4

from sentra_core.schemas.engine_event import EngineEvent
from sentra_brain_api.features.chat.mappers import engine_event_to_wire


def test_message_final_delivers_content():
    final_text = "Hello world!"
    evt = EngineEvent(
        event_id=uuid4().hex,
        timestamp=datetime.now(timezone.utc),
        type="message_final",
        author="assistant",
        content=final_text,
    )
    out = engine_event_to_wire(evt)
    assert out.type == "message_final"
    assert out.content == final_text

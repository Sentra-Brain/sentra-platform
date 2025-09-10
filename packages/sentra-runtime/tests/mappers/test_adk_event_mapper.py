from uuid import uuid4
from types import SimpleNamespace
from sentra.runtime.mappers import adk_event_mapper
from sentra.runtime.mappers.adk_event_mapper import from_adk, to_adk

def make_adk_event():
    # Simulate ADK event structure
    content_part = SimpleNamespace(text="hi")
    content = SimpleNamespace(role="user", parts=[content_part])
    return SimpleNamespace(
        id=str(uuid4()),
        invocation_id=None,
        timestamp=1234567890,
        author="user",
        type="message_final",
        partial=None,
        turn_complete=None,
        content=content,
        metadata={"foo": "bar"},
    )

def test_adk_to_sentra_roundtrip():
    adk_event = make_adk_event()
    sentra_event = from_adk(adk_event)
    assert sentra_event.author == adk_event.author
    assert sentra_event.content.parts[0].text == adk_event.content.parts[0].text
    # Now back to ADK
    adk2 = to_adk(sentra_event)
    adk_event_mapper.ADKEvent.assert_called_once()
    kwargs = adk_event_mapper.ADKEvent.call_args.kwargs
    assert kwargs["id"] == str(sentra_event.id)

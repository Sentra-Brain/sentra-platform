import anyio

from sentra_engine.app import run_conversation
from sentra_engine.models import ConversationEvent, ConversationRequest


def test_run_conversation_returns_event() -> None:
    request = ConversationRequest(messages=["hello"])
    event = anyio.run(run_conversation, request)
    assert isinstance(event, ConversationEvent)

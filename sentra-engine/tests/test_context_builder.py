from sentra_engine.context import build_context
from sentra_engine.models import ConversationRequest


def test_build_context_returns_dict() -> None:
    request = ConversationRequest(messages=["hi"])
    context = build_context(request)
    assert context == {}

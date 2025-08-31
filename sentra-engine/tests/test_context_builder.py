from sentra_engine.context import build_context
from sentra_engine.models import ConversationRequest


def test_build_context_returns_last_three_messages() -> None:
    request = ConversationRequest(messages=["a", "b", "c", "d"])
    context = build_context(request)
    assert context["history"] == "b\nc\nd"
    assert context["knowledge"] == "TODO: injected from RAGTool"

from sentra_engine.core.models import Message, PromptContext

def test_message_and_context_init():
    msg = Message(role="user", content="Hello")
    ctx = PromptContext(messages=[msg])
    assert ctx.messages[0].role == "user"
    assert ctx.messages[0].content == "Hello"

def test_model_equality():
    msg1 = Message(role="user", content="Hi")
    msg2 = Message(role="user", content="Hi")
    assert msg1 == msg2

import pytest
import pytest_asyncio
from sentra_engine.core.models import DeltaEvent, PromptContext, Message
from sentra_engine.conversation.entrypoint.conversation_engine import ConversationEngine
from sentra_engine.context.ports.context import ContextPort
from sentra_engine.llm.ports.llm import LLMPort
from sentra_engine.persistence.ports.persistence import PersistencePort

class FakePersistence(PersistencePort):
    def __init__(self):
        self.messages = []

    async def append_message(self, conversation_id, message):
        self.messages.append(message)

    async def load_conversation(self, conversation_id):
        return self.messages

    async def append_step_event(self, conversation_id, event):
        pass  # Not needed for this test

class FakeContext(ContextPort):
    async def build(self, conversation_id, rag_context=None):
        return PromptContext(messages=[
            Message(id="msg0", role="system", content="You are Sentra."),
        ])

class FakeLLM(LLMPort):
    async def chat_stream(self, prompt_context, tools_schema=None, guidance=None):
        yield DeltaEvent(type="message_delta", content="Hello ")
        yield DeltaEvent(type="message_delta", content="world!")

@pytest.mark.asyncio
async def test_run_fast():
    persistence = FakePersistence()
    context = FakeContext()
    llm = FakeLLM()

    engine = ConversationEngine(context=context, llm=llm, persistence=persistence)

    events = [event async for event in engine.run_fast(
        user_id="user1",
        conversation_id="conv1",
        message_id=None,
        response_message_id=None,
        content="Say something",
    )]

    assert [event.type for event in events] == ["message_delta", "message_delta", "message_final"]
    assert events[-1].content == "Hello world!"

    assert persistence.messages[0].role == "user"
    assert persistence.messages[1].role == "assistant"
    assert persistence.messages[1].content == "Hello world!"

import asyncio
from typing import AsyncGenerator, Optional, Sequence, Union, Mapping, Any

from sentra_engine.core.models import (
    DeltaEvent,
    Message,
    PromptContext,
    RAGContext,
    StepEvent,
)
from sentra_engine.conversation.adapters.engine import ConversationEngine
from sentra_engine.context.ports.context import ContextPort
from sentra_engine.llm.ports.llm import LLMPort
from sentra_engine.persistence.ports.persistence import PersistencePort
from sentra_engine.planner.ports.planner import PlannerPort


class AskingLLM(LLMPort):
    async def chat_stream(
        self,
        prompt_context: PromptContext,
        tools_schema=None,
        guidance: Optional[str] = None,
    ) -> AsyncGenerator[DeltaEvent, None]:
        yield DeltaEvent(type="message_delta", content="Which color?")
        return


class Ctx(ContextPort):
    async def build(
        self,
        conversation_id: str,
        rag_context: Optional[RAGContext] = None,
    ) -> PromptContext:
        return PromptContext(messages=[])


class Pers(PersistencePort):
    def __init__(self):
        self.msgs: list[Message] = []
        self.events: list[StepEvent] = []

    async def append_message(self, conversation_id: str, message: Message) -> None:
        self.msgs.append(message)

    async def append_step_event(self, conversation_id: str, event: StepEvent) -> None:
        self.events.append(event)

    async def load_conversation(
        self, conversation_id: str
    ) -> Sequence[Union[Message, Mapping[str, Any]]]:
        return []


class AskPlanner(PlannerPort):
    async def plan(self, transcript, context: str):
        return type("_", (), {"action": "AskParams", "params": {}})()


async def _run():
    engine = ConversationEngine(
        context=Ctx(),
        llm=AskingLLM(),
        persistence=Pers(),
        planner=AskPlanner(),
        tool_orchestrator=None,
    )
    chunks = []
    async for ev in engine.run_planner(
        user_id="u",
        conversation_id="c",
        message_id=None,
        response_message_id=None,
        content="hi",
    ):
        if ev.type == "message_delta":
            chunks.append(ev.content)
    assert "Which color?" in "".join(chunks)


def test_planner_ask_params():
    asyncio.run(_run())


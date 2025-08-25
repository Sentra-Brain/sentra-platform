import asyncio
from typing import AsyncGenerator, Optional, Sequence, Union, Mapping, Any

from sentra_engine.core.models import (
    DeltaEvent,
    Message,
    PromptContext,
    RAGContext,
    StepEvent,
    ToolResult,
    ToolSchema,
)
from sentra_engine.conversation.entrypoint.conversation_engine import ConversationEngine
from sentra_engine.context.ports.context import ContextPort
from sentra_engine.llm.ports.llm import LLMPort
from sentra_engine.mcp.ports.mcp import MCPPort
from sentra_engine.persistence.ports.persistence import PersistencePort
from sentra_engine.planner.ports.planner import PlannerPort
from sentra_engine.tools.adapters.orchestrator import ToolOrchestrator

class LLMWithTool(LLMPort):
    def __init__(self):
        self.round = 0

    async def chat_stream(
        self,
        prompt_context: PromptContext,
        tools_schema=None,
        guidance: Optional[str] = None,
    ) -> AsyncGenerator[DeltaEvent, None]:
        self.round += 1
        if self.round == 1:
            yield DeltaEvent(type="message_delta", content="I'll search that. ")
            yield DeltaEvent(
                type="tool_call_delta",
                metadata={"index": 0, "name": "echo", "arguments_delta": '{"text":"one"}'},
            )
            yield DeltaEvent(type="tool_calls_done")
            return
        if self.round == 2:
            yield DeltaEvent(type="message_delta", content="Searching again. ")
            yield DeltaEvent(
                type="tool_call_delta",
                metadata={"index": 0, "name": "echo", "arguments_delta": '{"text":"two"}'},
            )
            yield DeltaEvent(type="tool_calls_done")
            return
        yield DeltaEvent(type="message_delta", content="Here are the results.")
        return

class Ctx(ContextPort):
    async def build(self, conversation_id: str, rag_context: Optional[RAGContext] = None) -> PromptContext:
        return PromptContext(messages=[])

class Pers(PersistencePort):
    def __init__(self): self.msgs: list[Message] = []; self.events: list[StepEvent] = []
    async def append_message(self, conversation_id: str, message: Message) -> None: self.msgs.append(message)
    async def append_step_event(self, conversation_id: str, event: StepEvent) -> None: self.events.append(event)
    async def load_conversation(self, conversation_id: str) -> Sequence[Union[Message, Mapping[str, Any]]]: return []

class MCPFake(MCPPort):
    async def list_tools(self) -> Sequence[ToolSchema]:
        return [ToolSchema(name="echo", parameters={"type":"object","properties":{"text":{"type":"string"}},"required":["text"]})]
    async def call_tool(self, name: str, args: dict) -> ToolResult:
        return ToolResult(ok=True, content=args.get("text"))

class PlannerSeq(PlannerPort):
    def __init__(self):
        self.actions = [
            ("CallTool", {}),
            ("CallTool", {}),
            ("Respond", {}),
        ]

    async def plan(self, transcript, context: str):
        action, params = self.actions.pop(0)
        return type("_", (), {"action": action, "params": params})()


async def _run():
    p = Pers()
    engine = ConversationEngine(
        context=Ctx(),
        llm=LLMWithTool(),
        persistence=p,
        planner=PlannerSeq(),
        tool_orchestrator=ToolOrchestrator(mcp=MCPFake(), persistence=p, telemetry=None),
    )
    chunks = []
    async for ev in engine.run_planner(
        user_id="u",
        conversation_id="c",
        message_id=None,
        response_message_id=None,
        content="search X",
    ):
        if ev.type == "message_delta":
            chunks.append(ev.content)
    text = "".join(chunks)
    assert "I'll search" in text and "Searching again." in text and "Here are the results." in text
    assert sum(1 for m in p.msgs if m.role == "system") == 2


def test_autonomous_tool():
    asyncio.run(_run())

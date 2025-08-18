import asyncio
from typing import AsyncGenerator, Optional, Sequence, Union, Mapping, Any
from sentra_engine.engine.engine import ConversationEngine
from sentra_engine.core.models import PromptContext, DeltaEvent, ToolSchema, ToolResult, Message, StepEvent, RAGContext
from sentra_engine.ports.llm import LLMPort
from sentra_engine.ports.context import ContextPort
from sentra_engine.ports.mcp import MCPPort
from sentra_engine.ports.persistence import PersistencePort
from sentra_engine.core.tool_orchestrator import ToolOrchestrator

class LLMWithTool(LLMPort):
    def __init__(self): self.round = 0
    async def chat_stream(self, prompt_context: PromptContext, tools_schema=None, guidance: Optional[str] = None) -> AsyncGenerator[DeltaEvent, None]:
        self.round += 1
        if self.round == 1:
            yield DeltaEvent(type="message_delta", content="I will search. ")
            yield DeltaEvent(type="tool_call_delta", metadata={"index": 0, "name": "echo", "arguments_delta": '{"text":"ok"}'})
            yield DeltaEvent(type="tool_calls_done")
            return
        else:
            yield DeltaEvent(type="message_delta", content="Done.")
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

async def _run():
    engine = ConversationEngine(
        context=Ctx(),
        llm=LLMWithTool(),
        persistence=Pers(),
        planner=None,
        tool_orchestrator=ToolOrchestrator(mcp=MCPFake(), persistence=Pers(), telemetry=None),
    )
    chunks = []
    async for ev in engine.run_fast(user_id="u", conversation_id="c", message_id=None, response_message_id=None, content="go"):
        if ev.type == "message_delta":
            chunks.append(ev.content)
    text = "".join(chunks)
    assert "I will search." in text and "Done." in text

def test_fast_autonomous_tool():
    asyncio.run(_run())

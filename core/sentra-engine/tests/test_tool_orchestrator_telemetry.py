import asyncio
from typing import Optional, Sequence, Mapping, Any

from sentra_engine.core.models import ToolSchema, ToolResult, Message, StepEvent
from sentra_engine.tools.core.orchestrator import ToolOrchestrator
from sentra_engine.mcp.ports.mcp import MCPPort
from sentra_engine.persistence.ports.persistence import PersistencePort
from sentra_engine.tools.ports.telemetry import TelemetryPort


class MCPDummy(MCPPort):
    async def list_tools(self) -> Sequence[ToolSchema]:
        return [
            ToolSchema(
                name="echo",
                parameters={
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                },
            )
        ]

    async def call_tool(self, name: str, args: dict) -> ToolResult:
        return ToolResult(ok=True, content=args.get("text"))


class PersDummy(PersistencePort):
    async def append_message(self, conversation_id: str, message: Message) -> None:
        pass

    async def append_step_event(self, conversation_id: str, event: StepEvent) -> None:
        pass

    async def load_conversation(
        self, conversation_id: str
    ) -> Sequence[Mapping[str, Any] | Message]:
        return []


class TelemetryRecorder(TelemetryPort):
    def __init__(self) -> None:
        self.calls = []

    def step_start(self, step_id: str, meta: Optional[dict] = None) -> None:
        self.calls.append(("start", step_id, meta))

    def step_end(
        self, step_id: str, success: bool, meta: Optional[dict] = None
    ) -> None:
        self.calls.append(("end", step_id, success, meta))

    def record_exception(self, exc: Exception, meta: Optional[dict] = None) -> None:
        self.calls.append(("exception", exc, meta))


def _run() -> list:
    telemetry = TelemetryRecorder()
    orchestrator = ToolOrchestrator(
        mcp=MCPDummy(), persistence=PersDummy(), telemetry=telemetry
    )
    asyncio.run(
        orchestrator.execute_one(
            conversation_id="c", plan_step_id="p1", tool_name="echo", args={"text": "hi"}
        )
    )
    return telemetry.calls


def test_telemetry_includes_tool_name() -> None:
    calls = _run()
    assert calls[0] == ("start", "p1", {"tool": "echo"})
    assert calls[1] == ("end", "p1", True, {"tool": "echo"})

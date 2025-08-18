from __future__ import annotations
import json
import time
from typing import Any, Dict, Optional, Sequence
from jsonschema import validate, ValidationError
from sentra_engine.core.models import ToolSchema, ToolResult, StepEvent
from sentra_engine.ports.mcp import MCPPort
from sentra_engine.ports.persistence import PersistencePort
from sentra_engine.ports.telemetry import TelemetryPort

_MAX_BYTES = 8192

class ToolOrchestrator:
    def __init__(
        self,
        *,
        mcp: MCPPort,
        persistence: PersistencePort,
        telemetry: Optional[TelemetryPort] = None,
        enabled: bool = True,
    ):
        self.mcp = mcp
        self.persistence = persistence
        self.telemetry = telemetry
        self.enabled = enabled

    async def registry(self) -> Sequence[ToolSchema]:
        return await self.mcp.list_tools()

    async def execute_one(
        self,
        *,
        conversation_id: str,
        plan_step_id: str,
        tool_name: str,
        args: Dict[str, Any],
    ) -> ToolResult:
        step_meta = {"tool": tool_name, "plan_step_id": plan_step_id}
        if self.telemetry:
            self.telemetry.step_start(plan_step_id, step_meta)

        await self.persistence.append_step_event(conversation_id, StepEvent(
            type="tool_start",
            detail={"tool": tool_name, "plan_step_id": plan_step_id, "args": args},
        ))

        if not self.enabled:
            res = ToolResult(ok=False, content=None, error="tools_disabled")
            await self._finish(conversation_id, plan_step_id, res)
            return res

        schemas = await self.mcp.list_tools()
        schema = next((s for s in schemas if s.name == tool_name), None)
        if not schema:
            err = ToolResult(ok=False, content=None, error="tool_not_found")
            await self._finish(conversation_id, plan_step_id, err)
            return err

        # Validate args
        try:
            params_schema = schema.parameters or {"type": "object"}
            validate(instance=args or {}, schema=params_schema)
        except ValidationError as ve:
            err = ToolResult(ok=False, content=None, error=f"validation_error: {ve.message}")
            await self._finish(conversation_id, plan_step_id, err)
            return err

        # Execute
        try:
            res = await self.mcp.call_tool(tool_name, args or {})
        except Exception as e:
            res = ToolResult(ok=False, content=None, error=f"execution_error: {e}")

        await self._finish(conversation_id, plan_step_id, res)
        return res

    async def _finish(self, conversation_id: str, plan_step_id: str, res: ToolResult) -> None:
        if self.telemetry:
            self.telemetry.step_end(plan_step_id, res.ok, {"error": res.error} if res.error else None)
        await self.persistence.append_step_event(conversation_id, StepEvent(
            type="tool_end" if res.ok else "tool_error",
            detail={"plan_step_id": plan_step_id, "ok": res.ok, "error": res.error},
        ))

def normalize_tool_output(tool_name: str, content: Any) -> str:
    if isinstance(content, (dict, list)):
        text = json.dumps(content, ensure_ascii=False)
    else:
        text = str(content)
    b = text.encode("utf-8", errors="ignore")
    if len(b) > _MAX_BYTES:
        b = b[:_MAX_BYTES]
        text = b.decode("utf-8", errors="ignore") + "\n…[truncated]"
    return f"Tool '{tool_name}' output:\n{text}"

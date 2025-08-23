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
        self._cached_schemas: Optional[Sequence[ToolSchema]] = None

    async def _get_schemas(self) -> Sequence[ToolSchema]:
        """Fetch and cache tool schemas."""
        if self._cached_schemas is None:
            self._cached_schemas = await self.mcp.list_tools()
        return self._cached_schemas

    async def _log_telemetry(
        self,
        plan_step_id: str,
        tool_name: str,
        event_type: str,
        success: bool,
        error: Optional[str] = None,
    ):
        """Log telemetry events."""
        if self.telemetry:
            if event_type == "start":
                self.telemetry.step_start(plan_step_id, {"tool": tool_name})
            elif event_type == "end":
                meta = {"tool": tool_name}
                if error:
                    meta["error"] = error
                self.telemetry.step_end(plan_step_id, success, meta)

    async def _append_event(self, conversation_id: str, step_event: StepEvent):
        """Append step events to persistence."""
        await self.persistence.append_step_event(conversation_id, step_event)

    async def execute_one(
        self,
        *,
        conversation_id: str,
        plan_step_id: str,
        tool_name: str,
        args: Dict[str, Any],
        tool_call_id: str | None = None,
    ) -> ToolResult:
        await self._log_telemetry(plan_step_id, tool_name, "start", success=True)
        await self._append_event(conversation_id, StepEvent(
            type="tool_start",
            detail={"tool": tool_name, "plan_step_id": plan_step_id, "args": args, "tool_call_id": tool_call_id},
        ))

        if not self.enabled:
            res = ToolResult(ok=False, content=None, error="tools_disabled")
            await self._finish(conversation_id, plan_step_id, tool_name, res, tool_call_id)
            return res

        schemas = await self._get_schemas()
        schema = next((s for s in schemas if s.name == tool_name), None)
        if not schema:
            err = ToolResult(ok=False, content=None, error="tool_not_found")
            await self._finish(conversation_id, plan_step_id, tool_name, err, tool_call_id)
            return err

        # Validate args
        try:
            params_schema = schema.parameters or {"type": "object"}
            validate(instance=args or {}, schema=params_schema)
        except ValidationError as ve:
            err = ToolResult(ok=False, content=None, error=f"validation_error: {ve.message}")
            await self._finish(conversation_id, plan_step_id, tool_name, err, tool_call_id)
            return err

        # Execute
        try:
            res = await self.mcp.call_tool(tool_name, args or {})
        except Exception as e:
            res = ToolResult(ok=False, content=None, error=f"execution_error: {e}")

        await self._finish(conversation_id, plan_step_id, tool_name, res, tool_call_id)
        return res

    async def _finish(
        self,
        conversation_id: str,
        plan_step_id: str,
        tool_name: str,
        res: ToolResult,
        tool_call_id: str | None,
    ) -> None:
        await self._log_telemetry(plan_step_id, tool_name, "end", success=res.ok, error=res.error)
        await self._append_event(conversation_id, StepEvent(
            type="tool_end" if res.ok else "tool_error",
            detail={"plan_step_id": plan_step_id, "ok": res.ok, "error": res.error, "tool_call_id": tool_call_id},
        ))

    async def registry(self) -> Sequence[ToolSchema]:
        """Return the list of tool schemas, using cache if available."""
        return await self._get_schemas()

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

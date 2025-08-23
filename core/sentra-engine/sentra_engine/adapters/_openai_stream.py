from typing import Any, Dict, List, Optional, Sequence
from sentra_engine.core.models import ToolSchema


def with_guidance(messages: List[Dict[str, Any]], guidance: Optional[str]) -> List[Dict[str, Any]]:
    if guidance:
        return [{"role": "system", "content": f"Planner guidance:\n{guidance}"}] + messages
    return messages


def apply_tools(payload: Dict[str, Any], tools_schema: Optional[Sequence[ToolSchema]]) -> None:
    if not tools_schema:
        return
    payload["tools"] = [
        {
            "type": "function",
            "function": {
                "name": s.name,
                "description": (s.description or s.title or s.name),
                "parameters": s.parameters,
            },
        }
        for s in tools_schema
    ]
    payload["tool_choice"] = "auto"

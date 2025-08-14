# sentra_brain_api/core/conversation_engine/mcp/tool_mapping.py
import re
from typing import Any

def _sanitize_name(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]", "_", name.strip())
    return s[:64] or "tool"

def _ensure_object_schema(s: Any) -> dict:
    if not isinstance(s, dict):
        return {"type": "object", "properties": {}, "additionalProperties": True}
    t = s.get("type")
    if t is None or t != "object":
        s["type"] = "object"
    if "properties" not in s or not isinstance(s["properties"], dict):
        s["properties"] = {}
    if "additionalProperties" not in s:
        s["additionalProperties"] = True
    return s

def mcp_tools_to_openai_tools(mcp_tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tools = []
    for t in mcp_tools or []:
        name = _sanitize_name(t.get("name", "tool"))
        desc = t.get("description") or ""
        params = _ensure_object_schema(t.get("inputs") or {})
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": desc,
                "parameters": params,
            }
        })
    return tools

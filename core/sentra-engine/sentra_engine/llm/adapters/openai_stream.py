import re
from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Tuple
from sentra_engine.core.models import ToolSchema

_OPENAI_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def with_guidance(messages: List[Dict[str, Any]], guidance: Optional[str]) -> List[Dict[str, Any]]:
    """
    Prepend an OpenAI-style system message that carries planner guidance.

    Why:
      Several inference servers (OpenAI-compatible, vLLM, llama.cpp) rely on a
      system message to influence tool-use behavior. Supplying planner guidance
      here nudges the LLM to prefer tools when appropriate without altering the
      original transcript order.

    Args:
      messages: Chat messages in OpenAI format: [{"role": "...", "content": "..."}].
      guidance: Optional text guidance to inject at the beginning as a system message.

    Returns:
      A new message list. If `guidance` is truthy, the first element will be a
      system message containing the guidance; otherwise, the list is returned unchanged.
    """
    if guidance:
        return [{"role": "system", "content": f"Planner guidance:\n{guidance}"}] + messages
    return messages


def _normalize_tool_name(mcp_name: str) -> str:
    """
    Convert an MCP tool name to an OpenAI-compatible function name.

    Rules:
      - Replace any non [A-Za-z0-9_-] character (including dots) with underscores.
      - Truncate to 64 characters (OpenAI limit).
      - Guarantee non-empty output (fallback "tool").

    Args:
      mcp_name: Tool name coming from MCP (e.g., 'web.search.v1').

    Returns:
      A normalized, OpenAI-safe function name (e.g., 'web_search_v1').
    """
    norm = re.sub(r"[^A-Za-z0-9_-]", "_", mcp_name)[:64]
    return norm or "tool"


def _downgrade_json_schema(schema: dict) -> dict:
    """
    Convert a 2020-12-ish JSON Schema to a simpler draft-07-like shape for
    OpenAI/vLLM function-calling.

    Transformations:
      - Strip `$schema`, `$id`, `$defs` which can confuse servers.
      - Ensure the top-level is { "type": "object", "properties": {...}, "required": [...] }.
        If it's not an object, wrap it under {"value": <schema>} and require "value".
      - Replace `anyOf: [{...}, {"type":"null"}]` with the first non-null branch and
        mark the field optional (remove from `required`).
      - Default `additionalProperties` to False to reduce model ambiguity.

    Args:
      schema: A JSON-serializable dict coming from MCP tool `inputSchema`/parameters.

    Returns:
      A simplified schema compatible with OpenAI-style tool validation.
    """
    s = deepcopy(schema or {})
    s.pop("$schema", None)
    s.pop("$id", None)
    s.pop("$defs", None)

    if s.get("type") != "object":
        return {"type": "object", "properties": {"value": s}, "required": ["value"]}

    props = s.setdefault("properties", {})
    req = set(s.get("required", []))

    for key, spec in list(props.items()):
        if isinstance(spec, dict) and "anyOf" in spec:
            branches = [b for b in spec["anyOf"] if isinstance(b, dict)]
            non_null = next((b for b in branches if b.get("type") != "null"), None)
            if non_null:
                cleaned = dict(non_null)
                cleaned.pop("anyOf", None)
                props[key] = cleaned
                # treat as optional when a null branch was present
                req.discard(key)
            else:
                # Fall back to a simple string if branches are not usable
                props[key] = {"type": "string"}
                req.discard(key)

    s["required"] = list(req)
    s.setdefault("additionalProperties", False)
    return s


def apply_tools(
    payload: Dict[str, Any],
    tools_schema: Optional[Sequence[ToolSchema]],
) -> Dict[str, str]:
    """
    Inject OpenAI-style tool definitions into an LLM request payload and return a routing map.

    This function converts canonical MCP tool specifications (ToolSchema) into the
    OpenAI-compatible `tools` array (with `type: "function"`), normalizing names and
    simplifying parameter schemas so that llama-server/vLLM accept and the LLM can call them.

    Side effects:
      - Mutates `payload` to include:
          payload["tools"]      = [ ... OpenAI function specs ... ]
          payload["tool_choice"] = "auto"
      - Ensures function names are unique and OpenAI-safe.
      - Truncates overly long descriptions to 512 chars.

    Args:
      payload: Mutable request dict destined for an OpenAI-compatible chat endpoint.
      tools_schema: Iterable of ToolSchema objects (name, description/title, parameters).

    Returns:
      A map { llm_name -> mcp_name } to route tool calls from the LLM back to the MCP server.

    Notes:
      - Keep the returned mapping alongside your streaming handler; when the model emits
        a tool call with `function.name = llm_name`, look up the original MCP tool name
        to perform `tools/call` on your MCP server.
    """
    if not tools_schema:
        return {}

    tools: List[Dict[str, Any]] = []
    to_mcp: Dict[str, str] = {}

    used_llm_names = set()
    for spec in tools_schema:
        mcp_name = spec.name
        llm_name = _normalize_tool_name(mcp_name)

        # ensure uniqueness after normalization (collision-safe)
        if llm_name in used_llm_names:
            base = llm_name
            i = 2
            while llm_name in used_llm_names:
                suffix = f"_{i}"
                llm_name = base[: 64 - len(suffix)] + suffix
                i += 1
        used_llm_names.add(llm_name)
        to_mcp[llm_name] = mcp_name

        params = _downgrade_json_schema(getattr(spec, "parameters", None) or {})
        desc = (getattr(spec, "description", None) or getattr(spec, "title", None) or mcp_name)[:512]

        tools.append({
            "type": "function",
            "function": {
                "name": llm_name,
                "description": desc,
                "parameters": params,
            },
        })

    payload["tools"] = tools
    payload["tool_choice"] = "auto"
    return to_mcp

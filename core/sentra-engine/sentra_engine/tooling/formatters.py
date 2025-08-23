import json
_MAX_BYTES = 8192


def normalize_tool_output(tool_name: str, content: object) -> str:
    """Format any tool result (json/list/str) into a bounded system message."""
    if isinstance(content, (dict, list)):
        text = json.dumps(content, ensure_ascii=False)
    else:
        text = str(content)
    b = text.encode("utf-8", errors="ignore")
    if len(b) > _MAX_BYTES:
        b = b[:_MAX_BYTES]
        text = b.decode("utf-8", errors="ignore") + "\n…[truncated]"
    return f"Tool '{tool_name}' output:\n{text}"

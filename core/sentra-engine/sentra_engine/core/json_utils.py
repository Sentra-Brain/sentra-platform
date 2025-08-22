import json

__all__ = [
    "parse_json_safe",
    "extract_delta_content",
    "extract_tool_call_deltas",
    "extract_finish_reason",
    "parse_json_line",
    "strip_data_prefix",
]

def parse_json_safe(json_string: str) -> dict | None:
    """Safely parse a JSON string into a dictionary."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        return None

def extract_delta_content(obj: dict) -> str | None:
    """Extract delta content from a JSON object."""
    try:
        return obj.get("choices", [{}])[0].get("delta", {}).get("content")
    except Exception:
        return None

def extract_tool_call_deltas(obj: dict) -> list[dict]:
    """Return a list of partial tool-call deltas: {index, id?, name?, arguments_delta?}"""
    out: list[dict] = []
    try:
        delta = obj.get("choices", [{}])[0].get("delta", {})
        tcs = delta.get("tool_calls") or []
        for tc in tcs:
            rec: dict = {"index": tc.get("index")}
            fn = (tc.get("function") or {})
            if "name" in fn:
                rec["name"] = fn["name"]
            if "id" in tc:
                rec["id"] = tc["id"]
            d = tc.get("function", {}).get("arguments")
            if d:
                rec["arguments_delta"] = d
            out.append(rec)
    except Exception:
        pass
    return out

def extract_finish_reason(obj: dict) -> str | None:
    """Extract the finish reason from a JSON object."""
    try:
        return obj.get("choices", [{}])[0].get("finish_reason")
    except Exception:
        return None

def parse_json_line(stripped: str) -> dict | None:
    """Safely parse a JSON line into a dictionary."""
    try:
        return parse_json_safe(stripped)
    except Exception:
        return None

def strip_data_prefix(line: str) -> str:
    """Remove the 'data:' prefix from a line, if present."""
    if line.startswith("data:"):
        return line[len("data:"):].strip()
    return line.strip()

import json

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

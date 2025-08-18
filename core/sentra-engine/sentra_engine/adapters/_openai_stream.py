import json

def _strip_data_prefix(line: str) -> str:
    if line.startswith("data:"):
        return line[len("data:"):].strip()
    return line.strip()

def _parse_json_line(stripped: str) -> dict | None:
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return None

def _extract_delta_content_from_obj(obj: dict) -> str | None:
    try:
        return obj.get("choices", [{}])[0].get("delta", {}).get("content")
    except Exception:
        return None

def _extract_tool_call_deltas(obj: dict) -> list[dict]:
    """Return a list of partial tool-call deltas: {index,id?,name?,arguments_delta?}"""
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

def _extract_finish_reason(obj: dict) -> str | None:
    try:
        return obj.get("choices", [{}])[0].get("finish_reason")
    except Exception:
        return None

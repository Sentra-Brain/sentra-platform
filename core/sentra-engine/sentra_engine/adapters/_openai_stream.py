import json

def _strip_data_prefix(line: str) -> str:
    """Remove the 'data:' prefix from a line if present."""
    if line.startswith("data:"):
        return line[len("data:"):].strip()
    return line.strip()

def _extract_delta_content(json_line: str) -> str | None:
    """Extract 'choices[0].delta.content' from a JSON line."""
    try:
        data = json.loads(json_line)
        return data.get("choices", [{}])[0].get("delta", {}).get("content")
    except (json.JSONDecodeError, IndexError, AttributeError):
        return None

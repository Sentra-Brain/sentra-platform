from sentra_engine.core.json_utils import parse_json_safe, extract_delta_content, extract_tool_call_deltas

def _strip_data_prefix(line: str) -> str:
    if line.startswith("data:"):
        return line[len("data:"):].strip()
    return line.strip()

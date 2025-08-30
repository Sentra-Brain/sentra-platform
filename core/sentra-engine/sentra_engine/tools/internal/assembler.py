import json
from collections import OrderedDict
from typing import Dict, List, Any

from sentra_engine.core.tool_intent import ToolCallDelta, ToolIntent


class ToolCallAssembler:
    """Accumulates ToolCallDelta fragments into complete ToolIntent objects."""

    def __init__(self) -> None:
        self._buckets: Dict[str, Dict[str, Any]] = OrderedDict()

    @staticmethod
    def _bucket_key(d: ToolCallDelta) -> str:
        if d.id:
            return f"id:{d.id}"
        if d.index is not None:
            return f"ix:{d.index}"
        return "single"

    def add(self, d: ToolCallDelta) -> None:
        key = self._bucket_key(d)
        bucket = self._buckets.setdefault(key, {"id": d.id, "name": None, "args_fragments": []})
        if d.name:
            bucket["name"] = d.name
        if d.arguments_fragment:
            bucket["args_fragments"].append(d.arguments_fragment)

    def finalize(self) -> List[ToolIntent]:
        intents: List[ToolIntent] = []
        for bucket in self._buckets.values():
            raw = "".join(bucket["args_fragments"]) or "{}"
            try:
                args = json.loads(raw)
            except json.JSONDecodeError as e:
                raise ValueError(f"Malformed tool arguments JSON: {e.msg}") from e
            name = bucket.get("name")
            if not name:
                raise ValueError("Tool name missing in assembled call")
            intents.append(ToolIntent(id=bucket.get("id"), name=name, arguments=args))
        return intents


__all__ = ["ToolCallAssembler"]


from typing import Iterable, Optional, Protocol
import json

from sentra_engine.core.tool_intent import ToolCallDelta


class ToolDeltaExtractor(Protocol):
    def extract(self, provider_obj: dict) -> Iterable[ToolCallDelta]:
        ...


class OpenAIExtractor:
    def extract(self, obj: dict) -> Iterable[ToolCallDelta]:
        delta = obj["choices"][0]["delta"]
        for tc in delta.get("tool_calls", []):
            fn = tc.get("function") or {}
            yield ToolCallDelta(
                index=tc.get("index") if isinstance(tc.get("index"), int) else None,
                id=tc.get("id"),
                name=fn.get("name"),
                arguments_fragment=fn.get("arguments"),
            )


class PlainJSONExtractor:
    """Detect tool calls expressed as plaintext JSON blobs."""

    def extract_from_text(self, text: str) -> Optional[ToolCallDelta]:
        text = text.strip()
        if not (text.startswith("{") and text.endswith("}")):
            return None
        try:
            obj = json.loads(text)
        except Exception:
            return None

        name = obj.get("name") or obj.get("function") or obj.get("tool")
        if not isinstance(name, str):
            return None

        args = (
            obj.get("arguments")
            or obj.get("params")
            or obj.get("parameters")
        )
        if args is None:
            return None

        return ToolCallDelta(index=None, id=None, name=name, arguments_fragment=json.dumps(args))


__all__ = [
    "ToolDeltaExtractor",
    "OpenAIExtractor",
    "PlainJSONExtractor",
]


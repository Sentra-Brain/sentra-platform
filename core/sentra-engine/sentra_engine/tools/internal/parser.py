from typing import List
from sentra_engine.core.models import DeltaEvent
from sentra_engine.core.tool_intent import ToolCallDelta, ToolIntent
from sentra_engine.tools.internal.assembler import ToolCallAssembler
from sentra_engine.tools.internal.extractors import PlainJSONExtractor


class ToolStreamParser:
    """
    Accumulates streamed DeltaEvents to (a) collect text chunks and (b) assemble tool intents.
    Supports optional plaintext JSON fallback (e.g., {"name": "...", "arguments": {...}} in the model’s text).
    """

    def __init__(self, *, allow_plaintext_fallback: bool = False) -> None:
        self._assembler = ToolCallAssembler()
        self._plain = PlainJSONExtractor() if allow_plaintext_fallback else None
        self._chunks: List[str] = []

    def ingest(self, ev: DeltaEvent) -> None:
        if ev.type == "message_delta" and ev.content:
            self._chunks.append(ev.content)
            if self._plain:
                maybe = self._plain.extract_from_text(ev.content)
                if maybe:
                    self._assembler.add(maybe)
        elif ev.type == "tool_call_delta" and ev.metadata:
            self._assembler.add(
                ToolCallDelta(
                    index=ev.metadata.get("index") if isinstance(ev.metadata.get("index"), int) else None,
                    id=ev.metadata.get("id"),
                    name=ev.metadata.get("name"),
                    arguments_fragment=ev.metadata.get("arguments_delta"),
                )
            )
        # ignore others ("tool_calls_done" is just a hint; finalization still needed)

    def text(self) -> str:
        return "".join(self._chunks)

    def finalize_intents(self) -> List[ToolIntent]:
        try:
            return self._assembler.finalize()
        except ValueError:
            return []

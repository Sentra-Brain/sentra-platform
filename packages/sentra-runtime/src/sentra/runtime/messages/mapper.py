# sentra/runtime/messages/mapper.py
from __future__ import annotations
import json
import uuid
from typing import Any, Sequence
from sentra.runtime.messages.models import (
    MessageDelta,
    MessageCompleted,
    MessageError,
    AggregatedMessage,
)

class MessageMapper:
    """Convert internal Sentra agent updates into typed Sentra message events."""

    def __init__(self):
        self.sequence_counter = 0

    def _next_seq(self) -> int:
        self.sequence_counter += 1
        return self.sequence_counter

    def _item_id(self) -> str:
        return f"msg_{uuid.uuid4().hex[:8]}"

    async def convert_event(self, raw_event: Any) -> Sequence[MessageDelta | MessageError]:
        """Convert raw event (dict, str, model) into typed Sentra events."""
        seq = self._next_seq()

        # Text-only or dict → MessageDelta
        if isinstance(raw_event, str):
            return [MessageDelta(sequence_number=seq, content=raw_event, item_id=self._item_id())]

        if isinstance(raw_event, dict):
            if "error" in raw_event:
                return [MessageError(sequence_number=seq, error=raw_event["error"])]
            if "text" in raw_event:
                return [MessageDelta(sequence_number=seq, content=raw_event["text"], item_id=self._item_id())]
            return [MessageDelta(sequence_number=seq, content=json.dumps(raw_event), item_id=self._item_id())]

        # Fallback
        return [MessageDelta(sequence_number=seq, content=str(raw_event), item_id=self._item_id())]

    async def aggregate_to_response(self, events: Sequence[MessageDelta]) -> AggregatedMessage:
        """Aggregate all deltas into one message."""
        content = "".join(e.content for e in events if isinstance(e, MessageDelta))
        return AggregatedMessage(id=f"resp_{uuid.uuid4().hex[:8]}", content=content)

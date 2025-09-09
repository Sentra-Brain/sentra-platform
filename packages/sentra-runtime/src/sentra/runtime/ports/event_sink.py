# sentra/runtime/ports/event_sink.py
from typing import Protocol
from sentra.schemas import Event

class EventSink(Protocol):
    async def on_event(self, event: Event) -> None: ...

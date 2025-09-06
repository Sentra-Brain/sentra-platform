# sentra/runtime/ports/event_sink.py
from typing import Protocol
from sentra.runtime.models import EngineEvent

class EventSink(Protocol):
    async def on_event(self, event: EngineEvent) -> None: ...

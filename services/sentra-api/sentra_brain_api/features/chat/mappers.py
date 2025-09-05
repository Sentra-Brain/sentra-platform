from __future__ import annotations

from datetime import datetime

from sentra_core.schemas.engine_event import EngineEvent
from sentra_brain_api.features.chat.schemas import SessionEvent


def engine_event_to_wire(ev: EngineEvent) -> SessionEvent:
    """Serialize an ``EngineEvent`` for wire transmission."""
    data = ev.model_dump(exclude_none=True)
    ts = ev.timestamp
    if isinstance(ts, datetime):
        data["timestamp"] = ts.isoformat()
    else:
        data["timestamp"] = str(ts)
    return SessionEvent(**data)

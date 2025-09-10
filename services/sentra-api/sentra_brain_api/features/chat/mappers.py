# services/sentra-api/sentra_brain_api/features/chat/mappers.py
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sentra.domain.models.event import SentraEvent
from sentra_brain_api.features.chat.schemas import SessionEvent


def engine_event_to_wire(ev: SentraEvent) -> SessionEvent:
    """Serialize a SentraEvent (UUID-native) for wire transmission as SessionEvent DTO."""
    # Accepts SentraEvent (UUID-native)
    data = ev.model_dump(exclude_none=True)
    # Map UUID id to id (string)
    data["id"] = str(getattr(ev, "id", getattr(ev, "event_id", uuid4())))
    ts = getattr(ev, "timestamp", None)
    if isinstance(ts, datetime):
        data["timestamp"] = ts.isoformat()
    elif ts is not None:
        data["timestamp"] = str(ts)
    else:
        data["timestamp"] = datetime.now(timezone.utc).isoformat()
    return SessionEvent(**data)

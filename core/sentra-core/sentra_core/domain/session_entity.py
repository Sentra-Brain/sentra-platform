from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .event_entity import EventEntity


class SessionEntity(BaseModel):
    app_name: Optional[str] = None
    user_id: Optional[str] = None
    session_id: str
    events: list[EventEntity] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)
    last_update_time: datetime

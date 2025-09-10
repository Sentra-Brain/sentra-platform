# packages/sentra-domain/src/sentra/domain/models/session.py

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .event import SentraEvent


class SessionModel(BaseModel):
    app_name: Optional[str] = None
    user_id: Optional[str] = None
    session_id: str
    events: list[SentraEvent] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)
    last_update_time: datetime

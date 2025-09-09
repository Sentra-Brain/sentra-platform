# packages/sentra-domain/src/sentra/domain/models/event.py

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class EventActions(BaseModel):
    state_delta: dict[str, Any]


class EventMessage(BaseModel):
    id: Optional[str] = None
    role: Optional[str] = None
    response_to: Optional[str] = None


class EventModel(BaseModel):
    event_id: str
    timestamp: datetime
    type: str
    content: Optional[str] = None
    author: Optional[str] = None
    task_type: Optional[str] = None
    task_run_id: Optional[str] = None
    step_id: Optional[str] = None
    label: Optional[str] = None
    status: Optional[str] = None
    meta: dict[str, Any] = Field(default_factory=dict)
    actions: Optional[EventActions] = None
    message: Optional[EventMessage] = None

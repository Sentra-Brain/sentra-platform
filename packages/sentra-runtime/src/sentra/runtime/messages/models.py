# sentra/runtime/messages/models.py
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal

class BaseEvent(BaseModel):
    type: str
    sequence_number: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MessageDelta(BaseEvent):
    type: Literal["message.delta"] = "message.delta"
    role: Literal["assistant", "user"] = "assistant"
    content: str
    item_id: str

class MessageCompleted(BaseEvent):
    type: Literal["message.completed"] = "message.completed"
    item_id: str


class MessageError(BaseEvent):
    type: Literal["message.error"] = "message.error"
    error: str

class AggregatedMessage(BaseModel):
    id: str
    role: Literal["assistant", "user"] = "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

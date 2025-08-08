from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any
from datetime import datetime, timezone

class ConversationDelta(BaseModel):
    role: str = "assistant"
    content: str
    final: bool = False

class ConversationEvent(BaseModel):
    type: Literal["message_delta", "message_final", "step_start", "step_progress", "step_end", "step_error"]
    step_id: Optional[str] = None
    label: Optional[str] = None
    status: Optional[str] = None
    content: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ConversationResponse(BaseModel):
    content: str = Field(..., description="Final response content from the assistant.")

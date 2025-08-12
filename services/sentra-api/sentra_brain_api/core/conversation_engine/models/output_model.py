from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any
from datetime import datetime, timezone
import uuid

class ConversationEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    type: Literal[
        "message_delta",
        "message_final",
        "step_start",
        "step_progress",
        "step_end",
        "step_error"
    ]
    task_type: Optional[str] = None
    task_run_id: Optional[str] = None
    step_id: Optional[str] = None
    label: Optional[str] = None
    status: Optional[str] = None
    content: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Keep for backward compatibility
class ConversationDelta(BaseModel):
    role: str = "assistant"
    content: str
    final: bool = False

class ConversationResponse(BaseModel):
    content: str = Field(..., description="Final response content from the assistant.")

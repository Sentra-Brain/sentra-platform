# sentra_brain_api/features/chat/schemas.py
from enum import Enum
from typing import List, Optional, Literal, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

# ---------- Input ----------

class ConversationMode(str, Enum):
    FAST = "fast"
    PLAN = "plan"

class ConversationOptions(BaseModel):
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = None

class ConversationRequest(BaseModel):
    user_id: UUID = Field(..., description="ID of the user sending the message")
    conversation_id: UUID = Field(..., description="ID of the conversation")
    message_id: Optional[UUID] = Field(default=None, description="ID of the message being sent")
    response_message_id: Optional[UUID] = Field(default=None, description="Pre-assigned ID for the assistant response message")
    content: str = Field(..., description="Content of the message")
    model: Optional[str] = Field(default="sentra-brain", description="Model to use for the conversation")
    parent_message_id: Optional[UUID] = Field(default=None, description="ID of the parent message")
    intent_override: Optional[str] = Field(default=None, description="Intent to override")
    stream: Optional[bool] = Field(default=True, description="Whether to stream the response")
    mode: ConversationMode = Field(default=ConversationMode.FAST, description="Engine mode")
    options: Optional[ConversationOptions] = None
    context_source_ids: Optional[List[UUID]] = Field(default=None, description="RAG sources")
    context_document_ids: Optional[List[UUID]] = Field(default=None, description="RAG documents")

# ---------- Output (wire/SSE) ----------

def _ts() -> str: return datetime.now(timezone.utc).isoformat()

class PlanOutlineStep(BaseModel):
    step_id: str
    title: str
    description: str
    action: Literal["respond","tool","rag","think","ask_params"]
    args_hint: Optional[str] = None

class ConversationEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: str = Field(default_factory=_ts)
    type: Literal[
        "plan_outline",
        "step_start", "step_progress", "step_end", "step_error",
        "message_delta", "message_final",
    ]
    # legacy/common
    task_type: Optional[str] = None
    task_run_id: Optional[str] = None
    step_id: Optional[str] = None
    label: Optional[str] = None
    status: Optional[str] = None
    content: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    # correlation with planner
    plan_step_id: Optional[str] = None
    # outline payload
    steps: Optional[List[PlanOutlineStep]] = None

# ---- Backwards compatibility helpers
class ConversationDelta(BaseModel):
    role: str = "assistant"
    content: str
    final: bool = False

class ConversationResponse(BaseModel):
    content: str = Field(..., description="Final response content from the assistant.")

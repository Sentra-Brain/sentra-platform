# sentra_brain_api/features/chat/schemas.py
from enum import Enum
from typing import List, Optional, Literal, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from sentra.schemas import Event

# ---------- Input ----------

class SessionMode(str, Enum):
    FAST = "fast"
    PLAN = "plan"


class SessionOptions(BaseModel):
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = None


class SessionRequest(BaseModel):
    user_id: UUID = Field(..., description="ID of the user sending the message")
    session_id: UUID = Field(..., description="ID of the session")
    id: Optional[UUID] = Field(default=None, description="ID of the message being sent")
    response_id: Optional[UUID] = Field(
        default=None, description="Pre-assigned ID for the assistant response message"
    )
    content: str = Field(..., description="Content of the message")
    model: Optional[str] = Field(
        default="sentra-brain", description="Model to use for the session"
    )
    parent_id: Optional[UUID] = Field(
        default=None, description="ID of the parent message"
    )
    intent_override: Optional[str] = Field(
        default=None, description="Intent to override"
    )
    stream: Optional[bool] = Field(
        default=True, description="Whether to stream the response"
    )
    mode: SessionMode = Field(
        default=SessionMode.FAST, description="Engine mode"
    )
    options: Optional[SessionOptions] = None
    context_source_ids: Optional[List[UUID]] = Field(
        default=None, description="RAG sources"
    )
    context_document_ids: Optional[List[UUID]] = Field(
        default=None, description="RAG documents"
    )

# ---------- Output (wire/SSE) ----------



class PlanOutlineStep(BaseModel):
    step_id: str
    title: str
    description: str
    action: Literal["respond", "tool", "rag", "think", "ask_params"]
    args_hint: Optional[str] = None


class SessionEvent(Event):
    plan_step_id: Optional[str] = None
    steps: Optional[List[PlanOutlineStep]] = None


# ---- Backwards compatibility helpers
class SessionDelta(BaseModel):
    role: str = "assistant"
    content: str
    final: bool = False


class SessionResponse(BaseModel):
    content: str = Field(
        ..., description="Final response content from the assistant."
    )

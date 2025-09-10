# services/sentra-api/sentra_brain_api/features/chat/schemas.py
from enum import Enum
from typing import List, Optional, Literal, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

class SessionMode(str, Enum):
    FAST = "fast"
    PLAN = "plan"


class SessionOptions(BaseModel):
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = None


class ChatSendRequest(BaseModel):
    user_id: UUID = Field(..., description="ID of the user sending the message")
    session_id: UUID = Field(..., description="ID of the session")
    event_id: UUID = Field(..., description="ID of the user event being sent")
    content: str = Field(..., description="Content of the message")
    model: Optional[str] = Field(
        default="sentra-brain", description="Model to use for the session"
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


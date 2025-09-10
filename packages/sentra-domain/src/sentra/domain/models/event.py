# packages/sentra-domain/src/sentra/domain/models/event.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class SentraEventActions(BaseModel):
    state_delta: dict[str, Any] = Field(default_factory=dict)
    artifact_delta: dict[str, Any] = Field(default_factory=dict)
    transfer_to_agent: Optional[str] = None
    escalate: Optional[bool] = None
    skip_summarization: Optional[bool] = None


class SentraEventContentPart(BaseModel):
    text: Optional[str] = None
    function_call: Optional[dict[str, Any]] = None
    function_response: Optional[dict[str, Any]] = None


class SentraEventContent(BaseModel):
    role: Optional[str] = None  # “user” or agent name for history
    parts: list[SentraEventContentPart] = Field(default_factory=list)


class SentraEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    invocation_id: Optional[UUID] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    author: str
    type: str
    partial: Optional[bool] = None
    turn_complete: Optional[bool] = None

    content: Optional[SentraEventContent] = None
    actions: Optional[SentraEventActions] = None

    # Metadata
    task_type: Optional[str] = None
    task_run_id: Optional[UUID] = None
    step_id: Optional[UUID] = None
    label: Optional[str] = None
    status: Optional[str] = None
    meta: dict[str, Any] = Field(default_factory=dict)

    def is_final_response(self) -> bool:
        if self.partial:
            return False
        if self.actions and self.actions.skip_summarization:
            return True
        return True
    
    def to_mongo_dict(self) -> dict[str, Any]:
        data = self.model_dump(exclude_none=True)
        # Normalize UUIDs → str
        for field in ("id", "invocation_id", "task_run_id", "step_id"):
            if field in data and data[field] is not None:
                data[field] = str(data[field])
        # Normalize timestamp → ISO8601
        if "timestamp" in data and isinstance(data["timestamp"], datetime):
            data["timestamp"] = data["timestamp"].isoformat()
        return data
    
    @classmethod
    def user_message(cls, text: str, **kwargs) -> "SentraEvent":
        return cls(
            author="user",
            type="message_final",
            content=SentraEventContent(
                role="user",
                parts=[SentraEventContentPart(text=text)],
            ),
            **kwargs,
        )

    @classmethod
    def assistant_message(cls, text: str, **kwargs) -> "SentraEvent":
        return cls(
            author="assistant",
            type="message_final",
            content=SentraEventContent(
                role="assistant",
                parts=[SentraEventContentPart(text=text)],
            ),
            **kwargs,
        )

    @classmethod
    def error(cls, msg: str, **kwargs) -> "SentraEvent":
        return cls(
            author="system",
            type="step_error",
            content=SentraEventContent(
                role="system",
                parts=[SentraEventContentPart(text=msg)],
            ),
            **kwargs,
        )
# packages/sentra-domain/src/sentra/domain/models/event.py
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, alias_generators, ConfigDict


class SerializableModel(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
        ser_json_bytes='base64',
        val_json_bytes='base64',
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
    )
    
class SentraEventType(str, Enum):
    # Message lifecycle
    MESSAGE_DELTA = "message_delta"
    MESSAGE_FINAL = "message_final"
    ERROR = "error"

    # Agent lifecycle
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"

    # Execution steps
    STEP_START = "step_start"
    STEP_END = "step_end"
    CONTEXT_BUILT = "context_built"
    LLM_CALLED = "llm_called"


class SentraEventContentPart(SerializableModel): 
    text: Optional[str] = None
    function_call: Optional[dict[str, Any]] = None
    function_response: Optional[dict[str, Any]] = None


class SentraEventContent(SerializableModel):
    role: str  # "user", "assistant", or "system"
    parts: list[SentraEventContentPart] = Field(default_factory=list)


class SentraEvent(SerializableModel):
    # Core identity
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Core semantics
    author: str  # "user", "assistant", or "system"
    type: str    # e.g. "message_delta", "message_final", "step_start", etc.
    content: Optional[SentraEventContent] = None

    # Tracking & status
    task_run_id: Optional[str] = None
    status: Optional[str] = None
    meta: dict[str, Any] = Field(default_factory=dict)

    # ----------------- HELPERS -----------------
    def is_final_response(self) -> bool:
        return self.type == SentraEventType.MESSAGE_FINAL

    def to_mongo_dict(self) -> dict[str, Any]:
        data = self.model_dump(exclude_none=True)
        data["id"] = str(self.id)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    # ----------------- CONSTRUCTORS -----------------
    @classmethod
    def user_message(cls, text: str, **kwargs) -> SentraEvent:
        return cls(
            author="user",
            type=SentraEventType.MESSAGE_FINAL,
            content=SentraEventContent(role="user", parts=[SentraEventContentPart(text=text)]),
            **kwargs,
        )

    @classmethod
    def assistant_message(cls, text: str, **kwargs) -> SentraEvent:
        return cls(
            author="assistant",
            type=SentraEventType.MESSAGE_FINAL,
            content=SentraEventContent(role="assistant", parts=[SentraEventContentPart(text=text)]),
            **kwargs,
        )
    
    @classmethod
    def system_message(cls, text: str, type: SentraEventType, **kwargs) -> SentraEvent:
        return cls(
            author="system",
            type=type,
            content=SentraEventContent(
                role="system", 
                parts=[SentraEventContentPart(text=text)]
            ),
            **kwargs,
        )

    @classmethod
    def error(cls, msg: str, **kwargs) -> SentraEvent:
        return cls(
            author="system",
            type=SentraEventType.ERROR,
            content=SentraEventContent(role="system", parts=[SentraEventContentPart(text=msg)]),
            status="error",
            **kwargs,
        )

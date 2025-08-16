# sentra_engine/core/models.py
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class PromptContext:
    messages: list[Any]

@dataclass
class ToolSchema:
    name: str
    parameters: dict

@dataclass
class DeltaEvent:
    type: str
    content: Optional[str] = None
    metadata: Optional[dict] = None

@dataclass
class ToolResult:
    ok: bool
    content: Any
    error: Optional[str] = None

@dataclass
class RAGContext:
    chunks: list[Any]
    sources: list[Any]

@dataclass
class Message:
    id: str
    role: str
    content: str
    timestamp: Optional[str] = None
    meta: Optional[dict] = None

@dataclass
class StepEvent:
    type: str
    detail: dict

@dataclass
class Transcript:
    messages: list[Message]

@dataclass
class PlanStep:
    action: str
    params: dict

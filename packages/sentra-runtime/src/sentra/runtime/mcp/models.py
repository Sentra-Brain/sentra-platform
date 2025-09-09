# packages/sentra-runtime/src/sentra/runtime/mcp/models.py
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ToolSchema:
    name: str
    parameters: dict
    title: Optional[str] = None
    description: Optional[str] = None  

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

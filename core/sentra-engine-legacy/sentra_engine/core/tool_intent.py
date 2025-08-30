from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class ToolCallDelta:
    index: Optional[int]
    id: Optional[str]
    name: Optional[str]
    arguments_fragment: Optional[str]


@dataclass(frozen=True)
class ToolIntent:
    id: Optional[str]
    name: str
    arguments: Dict[str, Any]


__all__ = ["ToolCallDelta", "ToolIntent"]


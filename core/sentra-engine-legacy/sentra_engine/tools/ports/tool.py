# sentra_engine/tools/ports/tool.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Sequence
from sentra_engine.core.models import ToolSchema, ToolResult


class ToolPort(ABC):
    @abstractmethod
    async def execute_one(
        self,
        *,
        conversation_id: str,
        plan_step_id: str,
        tool_name: str,
        args: Dict[str, Any],
        tool_call_id: Optional[str] = None,
    ) -> ToolResult:
        """Execute a single tool call with arguments."""
        raise NotImplementedError

    @abstractmethod
    async def registry(self) -> Sequence[ToolSchema]:
        """Return the list of available tools."""
        raise NotImplementedError

    @abstractmethod
    def reset_registry_cache(self) -> None:
        """Clear the cached registry (if applicable)."""
        raise NotImplementedError

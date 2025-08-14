# sentra_engine/ports/mcp.py
from abc import ABC, abstractmethod
from typing import Sequence
from sentra_engine.core.models import ToolSchema, ToolResult


class MCPPort(ABC):
    @abstractmethod
    async def list_tools(self) -> Sequence[ToolSchema]:
        """Return the list of available MCP tools."""
        raise NotImplementedError

    @abstractmethod
    async def call_tool(self, name: str, args: dict) -> ToolResult:
        """Execute a tool with given name and arguments."""
        raise NotImplementedError

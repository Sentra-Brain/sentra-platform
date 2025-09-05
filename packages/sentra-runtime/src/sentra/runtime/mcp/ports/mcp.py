# sentra.runtime/ports/mcp.py
from abc import ABC, abstractmethod
from typing import Sequence

from sentra.runtime.mcp.models import ToolResult, ToolSchema


class MCPPort(ABC):
    @abstractmethod
    async def list_tools(self) -> Sequence[ToolSchema]:
        """Return the list of available MCP tools."""
        raise NotImplementedError

    @abstractmethod
    async def call_tool(self, name: str, args: dict) -> ToolResult:
        """Execute a tool with given name and arguments."""
        raise NotImplementedError

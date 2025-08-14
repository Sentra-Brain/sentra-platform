# sentra_brain_api/core/conversation_engine/mcp/sentra_mcp_client.py
from fastmcp.client import Client
from typing import Any
import os, asyncio

DEFAULT_MCP_URL = "http://sentra-mcp:8200/tools/mcp"  # <-- ojo: /tools/mcp

class SentraMCPClient:
    def __init__(self, base_url: str | None = None, *, request_timeout: float | None = 10.0):
        self.base_url = (base_url or os.getenv("SENTRA_MCP_URL", DEFAULT_MCP_URL)).rstrip("/")
        self.timeout = request_timeout
        self._cm: Client | None = None
        self._client: Client | None = None

    async def __aenter__(self):
        # Open persistent connection
        self._cm = Client(self.base_url, timeout=self.timeout)
        self._client = await self._cm.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # Close persistent connection
        if self._cm:
            await self._cm.__aexit__(exc_type, exc, tb)
        self._cm = None
        self._client = None

    async def list_tools(self) -> list[dict[str, Any]]:
        if not self._client:
            raise RuntimeError("MCP client not connected. Use 'async with SentraMCPClient(...)'.")
        tools = await self._client.list_tools()
        return [
            {
                "name": t.name,
                "description": getattr(t, "description", ""),
                "inputs": getattr(t, "inputSchema", {}) or {},
                "output": getattr(t, "outputSchema", {}) or {},
                "meta": getattr(t, "meta", {}) or {},
            }
            for t in tools
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if not self._client:
            raise RuntimeError("MCP client not connected. Use 'async with SentraMCPClient(...)'.")
        return await self._client.call_tool(name=name, arguments=arguments)

    async def healthcheck(self) -> bool:
        try:
            if self._client:
                await asyncio.wait_for(self._client.list_tools(), timeout=3.0)
            else:
                async with Client(self.base_url, timeout=self.timeout) as tmp:
                    await asyncio.wait_for(tmp.list_tools(), timeout=3.0)
            return True
        except Exception:
            return False

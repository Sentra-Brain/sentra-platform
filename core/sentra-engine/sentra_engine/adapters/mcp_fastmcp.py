import httpx
from typing import Sequence
from sentra_engine.ports.mcp import MCPPort
from sentra_engine.core.models import ToolSchema, ToolResult


class MCPProtocolAdapter(MCPPort):
    def __init__(self, base_url: str, *, request_timeout: float | None = None):
        self.base_url = base_url.rstrip("/")
        self.request_timeout = request_timeout

    async def list_tools(self) -> Sequence[ToolSchema]:
        url = f"{self.base_url}/tools/list"
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            resp = await client.post(url, json={})
            resp.raise_for_status()
            data = resp.json()
        tools = []
        for t in data.get("tools", []):
            tools.append(
                ToolSchema(
                    name=t.get("name"),
                    parameters=t.get("inputSchema") or t.get("parameters") or {},
                    title=t.get("title"),
                    description=t.get("description"),
                )
            )
        return tools

    async def call_tool(self, name: str, args: dict) -> ToolResult:
        url = f"{self.base_url}/tools/call"
        payload = {"name": name, "arguments": args}
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
        ok = not data.get("isError", False) and "error" not in data
        content = (
            data.get("data")
            or data.get("structuredContent")
            or data.get("content")
        )
        if isinstance(content, list) and len(content) == 1:
            block = content[0]
            if isinstance(block, dict) and block.get("type") == "text":
                content = block.get("text")
        return ToolResult(ok=ok, content=content, error=data.get("error"))

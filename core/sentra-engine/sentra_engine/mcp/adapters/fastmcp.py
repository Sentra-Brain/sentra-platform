import json
import uuid
import asyncio
from functools import lru_cache
from typing import Any, Dict, Optional, Sequence, cast

import httpx

from sentra_core.settings import settings
from sentra_engine.mcp.ports.mcp import MCPPort
from sentra_engine.core.models import ToolSchema, ToolResult

_PROTOCOL_VERSION = "2025-06-18"  # Aligns with your FastMCP server


class MCPProtocolAdapter(MCPPort):
    """
    Client for FastMCP using JSON-RPC over HTTP with optional SSE fallback.

    - Endpoint: POST {base_url}/mcp
    - Session: 'initialize' request → expect 'Mcp-Session-Id' in header
    - Fallback: Accepts 'application/json' or 'text/event-stream' responses
    """

    def __init__(self, base_url: str, *, request_timeout: Optional[float] = None):
        self.base_url = base_url.rstrip("/")
        self.request_timeout = request_timeout
        self._session_id: Optional[str] = None
        self._initialized: bool = False
        self._lock = asyncio.Lock()
        self._client: Optional[httpx.AsyncClient] = None

    async def startup(self) -> None:
        """Create HTTP client and initialize a session (idempotent)."""
        await self._ensure_client()
        assert self._client is not None
        async with self._lock:
            await self._ensure_initialized_locked(self._client)

    async def shutdown(self) -> None:
        """Shutdown the HTTP client and reset session state."""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._initialized = False
        self._session_id = None

    async def _ensure_client(self) -> None:
        if not self._client:
            self._client = httpx.AsyncClient(timeout=self.request_timeout)

    async def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "MCP-Protocol-Version": _PROTOCOL_VERSION,
        }
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        return headers

    @staticmethod
    def _parse_json_or_sse_text(text: str) -> Dict[str, Any]:
        t = (text or "").strip()
        if t.startswith("{"):
            return cast(Dict[str, Any], json.loads(t))

        data_json: Optional[str] = None
        for line in t.splitlines():
            if line.strip().startswith("data:"):
                payload = line[5:].strip()
                if payload:
                    data_json = payload
        if not data_json:
            raise RuntimeError("Response is not JSON or SSE with 'data:' field")
        return cast(Dict[str, Any], json.loads(data_json))

    async def _post_rpc(self, client: httpx.AsyncClient, body: Dict[str, Any]) -> Dict[str, Any]:
        resp = await client.post(self.base_url, json=body, headers=await self._headers())
        resp.raise_for_status()
        content_type = (resp.headers.get("content-type") or "").lower()

        if "application/json" in content_type:
            data = cast(Dict[str, Any], resp.json())
        else:
            data = self._parse_json_or_sse_text(resp.text)

        if "error" in data:
            raise RuntimeError(f"MCP error: {data['error']}")
        return cast(Dict[str, Any], data.get("result") or data)

    async def _ensure_initialized(self, client: httpx.AsyncClient) -> None:
        if self._initialized:
            return
        async with self._lock:
            if self._initialized:
                return
            await self._ensure_initialized_locked(client)

    async def _ensure_initialized_locked(self, client: httpx.AsyncClient) -> None:
        init_body: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {
                "protocolVersion": _PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "sentra-engine", "version": "0.1.0"},
            },
        }

        resp = await client.post(self.base_url, json=init_body, headers=await self._headers())
        resp.raise_for_status()

        self._session_id = (
            resp.headers.get("Mcp-Session-Id")
            or resp.headers.get("MCP-Session-Id")
            or resp.headers.get("mcp-session-id")
        )
        if not self._session_id:
            _ = resp.text
            raise RuntimeError("Missing Mcp-Session-Id in 'initialize' response")

        notify = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        resp2 = await client.post(self.base_url, json=notify, headers=await self._headers())
        resp2.raise_for_status()

        self._initialized = True

    async def _rpc_with_reinit(self, body: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_client()
        assert self._client is not None
        client = self._client
        try:
            await self._ensure_initialized(client)
            return await self._post_rpc(client, body)
        except Exception as e:
            s = str(e)
            if ("Missing session ID" in s) or ("session" in s and "missing" in s) or ("401" in s) or ("440" in s):
                self._initialized = False
                self._session_id = None
                await self._ensure_initialized(client)
                return await self._post_rpc(client, body)
            raise

    # ────────────────────────── MCPPort Methods ──────────────────────────

    async def list_tools(self) -> Sequence[ToolSchema]:
        body = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/list",
            "params": {},
        }
        result = await self._rpc_with_reinit(body)

        tools: list[ToolSchema] = []
        for t in (result.get("tools") or []):
            tools.append(
                ToolSchema(
                    name=str(t.get("name") or ""),
                    parameters=cast(Dict[str, Any], t.get("inputSchema") or t.get("parameters") or {"type": "object"}),
                    title=cast(Optional[str], t.get("title")),
                    description=cast(Optional[str], t.get("description")),
                )
            )
        return tools

    async def call_tool(self, name: str, args: Dict[str, Any]) -> ToolResult:
        body = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {"name": name, "arguments": args or {}},
        }
        result = await self._rpc_with_reinit(body)

        content: Any = (
            result.get("data")
            or result.get("structuredContent")
            or result.get("content")
            or result.get("result")
        )

        if (
            isinstance(content, list)
            and len(content) == 1
            and isinstance(content[0], dict)
            and content[0].get("type") == "text"
        ):
            content = content[0].get("text")

        err_val = result.get("error")
        if isinstance(err_val, dict) and "message" in err_val:
            err_val = err_val.get("message")

        ok = not result.get("isError", False) and not err_val

        return ToolResult(ok=ok, content=content, error=cast(Optional[str], err_val))


@lru_cache(maxsize=1)
def get_mcp() -> MCPProtocolAdapter:
    """Singleton instance of MCP client."""
    return MCPProtocolAdapter(
        base_url=settings.mcp_base_url,
        request_timeout=settings.mcp_timeout,
    )

# sentra_engine/adapters/mcp_fastmcp.py
import uuid
from typing import Any, Dict, Optional, Sequence, cast

import httpx

from sentra_engine.ports.mcp import MCPPort
from sentra_engine.core.models import ToolSchema, ToolResult

_PROTOCOL_VERSION = "2025-06-18"  # keep in sync with your server


class MCPProtocolAdapter(MCPPort):
    """
    FastMCP over HTTP/Streamable-HTTP speaks JSON-RPC on a single endpoint (e.g. /mcp)
    and requires a session handshake:
      1) POST 'initialize' to /mcp
      2) Read 'Mcp-Session-Id' response header
      3) Include that header on subsequent JSON-RPC calls (tools/list, tools/call, ...)
    """

    def __init__(self, base_url: str, *, request_timeout: Optional[float] = None):
        # IMPORTANT: base_url must point to the MCP JSON-RPC endpoint, e.g. http://sentra-mcp:8200/mcp
        self.base_url: str = base_url.rstrip("/")
        self.request_timeout: Optional[float] = request_timeout
        self._session_id: Optional[str] = None

    async def _headers(self) -> Dict[str, str]:
        h: Dict[str, str] = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "MCP-Protocol-Version": _PROTOCOL_VERSION,
        }
        if self._session_id is not None:
            # Narrow Optional[str] -> str for the headers mapping
            h["Mcp-Session-Id"] = cast(str, self._session_id)
        return h

    async def _init_session(self, client: httpx.AsyncClient) -> None:
        if self._session_id:
            return
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
        r = await client.post(self.base_url, json=init_body, headers=await self._headers())
        r.raise_for_status()

        # Extract session id from headers (case-insensitive convenience)
        session_id: Optional[str] = None
        for key in ("Mcp-Session-Id", "MCP-Session-Id", "mcp-session-id"):
            val = r.headers.get(key)
            if val:
                session_id = val
                break
        self._session_id = session_id

        # Optional but polite per MCP: notify initialized if we have a session
        if self._session_id:
            await client.post(
                self.base_url,
                json={"jsonrpc": "2.0", "method": "notifications/initialized", "id": str(uuid.uuid4())},
                headers=await self._headers(),
            )

    async def _rpc(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform a JSON-RPC call with automatic session initialization and a single retry
        if the server responds as if the session is missing/expired.
        """
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            # Ensure session first
            await self._init_session(client)

            body: Dict[str, Any] = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method}
            if params is not None:
                body["params"] = params

            resp = await client.post(self.base_url, json=body, headers=await self._headers())

            # If route/session handling on the server dropped our session, try once more
            if resp.status_code in (404, 410):
                # Reset and re-init, then retry once
                self._session_id = None
                await self._init_session(client)
                resp = await client.post(self.base_url, json=body, headers=await self._headers())

            resp.raise_for_status()
            data: Dict[str, Any] = resp.json()

            # JSON-RPC error shape: {"jsonrpc":"2.0","id":...,"error": {...}}
            if "error" in data:
                raise RuntimeError(f"MCP error: {data['error']}")

            # Some servers return {"result": {...}}; normalize to the result object
            result = cast(Dict[str, Any], data.get("result") or data)
            return result

    # ──────────────────────────────────────────────────────────────────────────
    # MCPPort implementation
    # ──────────────────────────────────────────────────────────────────────────

    async def list_tools(self) -> Sequence[ToolSchema]:
        result = await self._rpc("tools/list")
        tools_list = cast(Sequence[Dict[str, Any]], result.get("tools") or [])
        out: list[ToolSchema] = []
        for t in tools_list:
            out.append(
                ToolSchema(
                    name=str(t.get("name") or ""),
                    parameters=cast(Dict[str, Any], t.get("inputSchema") or t.get("parameters") or {"type": "object"}),
                    title=cast(Optional[str], t.get("title")),
                    description=cast(Optional[str], t.get("description")),
                )
            )
        return out

    async def call_tool(self, name: str, args: Dict[str, Any]) -> ToolResult:
        result = await self._rpc("tools/call", {"name": name, "arguments": args or {}})

        # FastMCP tool result variants
        ok: bool = not bool(result.get("isError", False)) and ("error" not in result)

        content: Any = (
            result.get("data")
            or result.get("structuredContent")
            or result.get("content")
        )

        # Unwrap common content-block shape: [{"type": "text", "text": "..."}]
        if isinstance(content, list) and len(content) == 1:
            block = content[0]
            if isinstance(block, dict) and block.get("type") == "text":
                content = block.get("text")

        return ToolResult(ok=ok, content=content, error=cast(Optional[str], result.get("error")))

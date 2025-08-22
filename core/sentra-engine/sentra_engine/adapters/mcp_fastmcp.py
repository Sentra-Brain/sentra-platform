import json
import uuid
from typing import Any, Dict, Optional, Sequence, cast

import httpx

from sentra_engine.ports.mcp import MCPPort
from sentra_engine.core.models import ToolSchema, ToolResult

_PROTOCOL_VERSION = "2025-06-18"  # alinea con tu server


class MCPProtocolAdapter(MCPPort):
    """
    Cliente MCP para FastMCP sobre HTTP con fallback SSE.
    - Endpoint único JSON-RPC: POST {base_url}/mcp
    - Handshake: initialize (request con id) -> notifications/initialized (notificación sin id/params)
    - Headers: Mcp-Session-Id en todas las peticiones tras initialize
    - Respuestas: intenta JSON; si viene SSE, extrae el último 'data: {...}'
    """

    def __init__(self, base_url: str, *, request_timeout: Optional[float] = None):
        self.base_url = base_url.rstrip("/")
        self.request_timeout = request_timeout
        self._session_id: Optional[str] = None
        self._initialized: bool = False

    # ─────────────────────────── utils ───────────────────────────
    async def _headers(self) -> Dict[str, str]:
        # Acepta JSON y SSE; Streamable-HTTP suele exigir text/event-stream
        h: Dict[str, str] = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "MCP-Protocol-Version": _PROTOCOL_VERSION,
        }
        if self._session_id:
             h["Mcp-Session-Id"] = self._session_id
        return h

    @staticmethod
    def _parse_json_or_sse_text(text: str) -> Dict[str, Any]:
        """
        Si 'text' empieza por '{', parsea como JSON.
        Si contiene frames SSE, toma el ÚLTIMO 'data: {...}' y parsea.
        """
        t = (text or "").strip()
        if t.startswith("{"):
            return cast(Dict[str, Any], json.loads(t))

        data_json: Optional[str] = None
        for raw_line in t.splitlines():
            line = raw_line.strip()
            if line.startswith("data:"):
                payload = line[5:].strip()
                if payload:
                    data_json = payload
        if not data_json:
            raise RuntimeError("Respuesta no es JSON ni SSE 'data:' con JSON")
        return cast(Dict[str, Any], json.loads(data_json))

    async def _post_rpc(self, client: httpx.AsyncClient, body: Dict[str, Any]) -> Dict[str, Any]:
        resp = await client.post(self.base_url, json=body, headers=await self._headers())
        resp.raise_for_status()

        ctype = (resp.headers.get("content-type") or "").lower()
        if "application/json" in ctype:
            data = cast(Dict[str, Any], resp.json())
        else:
            # Algunos FastMCP responden text/event-stream incluso en HTTP
            data = self._parse_json_or_sse_text(resp.text)

        if "error" in data:
            # JSON-RPC error
            raise RuntimeError(f"MCP error: {data['error']}")
        return cast(Dict[str, Any], data.get("result") or data)

    async def _ensure_initialized(self, client: httpx.AsyncClient) -> None:
        if self._initialized:
            return

        # 1) initialize (request con id y params)
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

        # Extrae session id del header (case-insensitive)
        self._session_id = (
            resp.headers.get("Mcp-Session-Id")
            or resp.headers.get("MCP-Session-Id")
            or resp.headers.get("mcp-session-id")
        )
        if not self._session_id:
            # Forzamos lectura del body para diagnósticos útiles
            _ = resp.text
            raise RuntimeError("No Mcp-Session-Id en la respuesta a 'initialize'")

        # 2) notifications/initialized (NOTIFICACIÓN: sin id, sin params)
        notify = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        resp2 = await client.post(self.base_url, json=notify, headers=await self._headers())
        resp2.raise_for_status()
        self._initialized = True

    # ──────────────────────── MCPPort impl ────────────────────────

    async def list_tools(self) -> Sequence[ToolSchema]:
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            await self._ensure_initialized(client)
            body = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "tools/list", "params": {}}
            result = await self._post_rpc(client, body)

        out: list[ToolSchema] = []
        for t in (result.get("tools") or []):
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
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            await self._ensure_initialized(client)
            body = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {"name": name, "arguments": args or {}},
            }
            result = await self._post_rpc(client, body)

        # FastMCP puede devolver varias formas:
        #  - {"data": ...}                    (datos nativos)
        #  - {"structuredContent": [...]}     (bloques MCP)
        #  - {"content": [...]}               (bloques)
        #  - {"result": {.../[/...]}          (cuando x-fastmcp-wrap-result = true)
        content: Any = (
            result.get("data")
            or result.get("structuredContent")
            or result.get("content")
            or result.get("result")
        )

        # Si es un vector de bloques MCP y solo hay uno de texto, desenvuelve a str
        if (
            isinstance(content, list)
            and len(content) == 1
            and isinstance(content[0], dict)
            and content[0].get("type") == "text"
        ):
            content = content[0].get("text")

        # Error “suave” (campo 'error' en result) y bandera 'isError'
        err_val = result.get("error")
        if isinstance(err_val, dict) and "message" in err_val:
            err_val = err_val.get("message")
        ok = not result.get("isError", False) and not err_val

        return ToolResult(ok=ok, content=content, error=cast(Optional[str], err_val))

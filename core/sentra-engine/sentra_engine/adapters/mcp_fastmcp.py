from __future__ import annotations
import time
import httpx
from typing import Any, Dict, List, Optional, Sequence
from sentra_engine.core.models import ToolSchema, ToolResult
from sentra_engine.ports.mcp import MCPPort

class MCPFastMCPAdapter(MCPPort):
    def __init__(self, base_url: str, *, ttl_secs: int = 60, client: Optional[httpx.AsyncClient] = None):
        self.base_url = base_url.rstrip("/")
        self._ttl = ttl_secs
        self._client = client
        self._cache: List[ToolSchema] | None = None
        self._cache_ts: float = 0.0
        self._stats = {"registry_fetches": 0}

    async def list_tools(self) -> Sequence[ToolSchema]:
        now = time.time()
        if self._cache and (now - self._cache_ts) < self._ttl:
            return self._cache
        async with self._ensure_client() as client:
            r = await client.get(f"{self.base_url}/tools/registry")
            r.raise_for_status()
            data = r.json()
            self._stats["registry_fetches"] += 1
            self._cache = [ToolSchema(name=i["name"], parameters=i.get("parameters", {})) for i in data]
            self._cache_ts = now
            return self._cache

    async def call_tool(self, name: str, args: dict) -> ToolResult:
        async with self._ensure_client() as client:
            r = await client.post(f"{self.base_url}/tools/run", json={"name": name, "args": args or {}})
            ok = r.status_code == 200 and (r.json().get("ok") is True)
            data = r.json()
            if ok:
                return ToolResult(ok=True, content=data.get("content"))
            return ToolResult(ok=False, content=None, error=data.get("error") or f"http_{r.status_code}")

    def _ensure_client(self):
        return self._client if self._client else httpx.AsyncClient(timeout=10)

    # testing helpers
    @property
    def stats(self) -> dict:
        return dict(self._stats)

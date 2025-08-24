from functools import lru_cache
from sentra_core.core.settings import settings
from sentra_engine.adapters.mcp_fastmcp import MCPProtocolAdapter

@lru_cache(maxsize=1)
def get_mcp() -> MCPProtocolAdapter:
    """Process-scoped MCP client instance (create once)."""
    return MCPProtocolAdapter(
        base_url=settings.mcp_base_url,
        request_timeout=settings.mcp_timeout,
    )

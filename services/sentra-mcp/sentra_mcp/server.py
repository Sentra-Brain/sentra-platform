# sentra_mcp/main.py
import os
from typing import Literal, cast

from sentra_core.core.logging import get_logger, configure_logging
from fastmcp import FastMCP
from sentra_mcp.tools_registry import register_all_tools

# Accepted transport literals for FastMCP.run(...)
TransportT = Literal["stdio", "http", "sse", "streamable-http"]

logger = get_logger(__name__)

def _normalize_transport(raw: str | None) -> TransportT:
    """
    Normalize env value to allowed literals. Defaults to 'http' if missing/unknown.
    """
    if not raw:
        return cast(TransportT, "http")

    r = raw.strip().lower()
    synonyms: dict[str, TransportT] = {
        "stdio": "stdio",
        "http": "http",
        "sse": "sse",
        "streamable-http": "streamable-http",
        "streamable_http": "streamable-http",
    }

    normalized = synonyms.get(r)
    if normalized is None:
        logger.warning("Unknown MCP_TRANSPORT '%s'; defaulting to 'http'", raw)
        normalized = "http"

    return cast(TransportT, normalized)

def build_mcp() -> FastMCP:
    mcp = FastMCP(name="Sentra MCP")
    register_all_tools(mcp)
    return mcp

def main():
    # --- your debug / logging style preserved ---
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    configure_logging(debug=debug_mode)

    if debug_mode:
        logger.info("🛠️ Debug mode enabled — waiting for debugger on port 5681")
        import debugpy  # type: ignore
        debugpy.listen(("0.0.0.0", 5681))
        debugpy.wait_for_client()

    # Optional envs (you don't need to add them to your .env — defaults are fine)
    transport_env = os.getenv("MCP_TRANSPORT", "http")
    host_env = os.getenv("MCP_HOST", "0.0.0.0")
    port_env = int(os.getenv("MCP_PORT", "8200"))

    transport: TransportT = _normalize_transport(transport_env)

    # Host/port only make sense for HTTP-like transports
    host = host_env if transport in ("http", "sse", "streamable-http") else None
    port = port_env if transport in ("http", "sse", "streamable-http") else None

    mcp = build_mcp()
    logger.info("🚀 Starting Sentra MCP (transport=%s host=%s port=%s)", transport, host, port)

    # Run the MCP server; default HTTP base path is /mcp
    mcp.run(transport=transport, host=host, port=port)

if __name__ == "__main__":
    main()

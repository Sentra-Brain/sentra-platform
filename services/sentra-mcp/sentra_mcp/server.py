# sentra_mcp/main.py
import os
from typing import Literal, cast

from sentra_core.core.logging import get_logger, configure_logging
from fastmcp import FastMCP
from sentra_mcp.tools_registry import register_all_tools

TransportT = Literal["stdio", "http", "sse", "streamable-http"]

logger = get_logger(__name__)

def _normalize_transport(raw: str | None) -> TransportT:
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
    norm = synonyms.get(r)
    if norm is None:
        logger.warning("Unknown MCP_TRANSPORT '%s'; defaulting to 'http'", raw)
        norm = "http"
    return cast(TransportT, norm)

def build_mcp() -> FastMCP:
    mcp = FastMCP(name="Sentra MCP")
    register_all_tools(mcp)
    return mcp

def main():
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    configure_logging(debug=debug_mode)

    if debug_mode:
        try:
            import debugpy  # type: ignore
            logger.info("🛠️ Debug mode: debugger on 0.0.0.0:5681")
            debugpy.listen(("0.0.0.0", 5681))
            if os.getenv("DEBUG_WAIT_FOR_CLIENT", "true").lower() == "true":
                logger.info("⏸️ Waiting for debugger to attach...")
                debugpy.wait_for_client()

        except Exception as e:
            logger.warning("Could not init debugpy: %s", e) 

    transport: TransportT = _normalize_transport(os.getenv("MCP_TRANSPORT"))
    host = os.getenv("MCP_HOST", "0.0.0.0") if transport in ("http", "sse", "streamable-http") else None
    port = int(os.getenv("MCP_PORT", "8200")) if transport in ("http", "sse", "streamable-http") else None

    mcp = build_mcp()
    logger.info("🚀 Starting Sentra MCP (transport=%s host=%s port=%s)", transport, host, port)
    mcp.run(transport=transport, host=host, port=port)

if __name__ == "__main__":
    main()

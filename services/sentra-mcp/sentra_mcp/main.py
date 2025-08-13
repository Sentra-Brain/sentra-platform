from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager
from sentra_core.core import logging
from sentra_mcp.tools_registry import register_all_tools
from fastmcp import FastMCP

import os

logger = logging.get_logger("sentra_mcp")

# Create the MCP server and register tools
mcp = FastMCP(name="Sentra MCP")
register_all_tools(mcp)

# Create the FastAPI app that wraps the MCP tools
mcp_app = mcp.http_app(path="/mcp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to initialize MCP and register tools."""
    # Initialize MCP and register tools
    async with mcp_app.lifespan(app):
        logger.info("🚀 Starting sentra-mcp...")

        app.state.mcp = mcp

        try:
            tools = await mcp.get_tools()
            logger.info(f"✅ Registered MCP tools: {list(tools.keys())}")
        except Exception as e:
            logger.warning(f"⚠️ Could not list tools: {e}")

        yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Sentra MCP Server",
        description="Exposes tools to Sentra Brain via FastMCP protocol.",
        version=os.getenv("API_VERSION", "0.1.0"),
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https?://(127\\.0\\.0\\.1|localhost)(:\\d{1,5})?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Mount MCP under /tools
    app.mount("/tools", mcp_app)

    @app.get("/", include_in_schema=False)
    async def redirect_to_docs():
        return RedirectResponse("/docs")
    

    @app.get("/health", tags=["system"])
    async def health():
        return {"status": "ok"}

    @app.get("/tools", tags=["system"])
    async def list_tools():
        try:
            tools = await app.state.mcp.get_tools()
            return JSONResponse([tool.dict(include={"name", "description"}) for tool in tools.values()])
        except Exception as e:
            logger.warning(f"⚠️ Failed to get tools: {e}")
            return JSONResponse({"error": "Failed to retrieve tools"}, status_code=500)

    # Uncomment when observability is ready
    # if os.getenv("TESTING") != "true":
    #     instrument_app(app)
    #     add_correlation_id_middleware(app)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logging.configure_logging(debug=debug_mode)

    if debug_mode:
        logger.info("🛠️ Debug mode enabled — waiting for debugger on port 5681")
        import debugpy
        debugpy.listen(("0.0.0.0", 5681))
        debugpy.wait_for_client()

    uvicorn.run(app, host="0.0.0.0", port=8200, log_level="debug" if debug_mode else "info")

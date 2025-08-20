# sentra_mcp/tools_registry.py
from fastmcp import FastMCP
from sentra_mcp.tools.web import register_web_tools
# from sentra_mcp.tools.kb import register_kb_tools
# from sentra_mcp.tools.fs import register_fs_tools

def register_all_tools(mcp: FastMCP) -> None:
    """Register all Sentra MCP tools with the provided FastMCP instance."""
    register_web_tools(mcp)
    # register_kb_tools(mcp)
    # register_fs_tools(mcp)

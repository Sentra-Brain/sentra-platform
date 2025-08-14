from fastmcp import FastMCP
from sentra_mcp.tools.web import register_web_tools
# from sentra_mcp.tools.kb import register_kb_tools  # Future
# from sentra_mcp.tools.fs import register_fs_tools  # Future

def register_all_tools(mcp: FastMCP):
    register_web_tools(mcp)
    # register_kb_tools(mcp)
    # register_fs_tools(mcp)

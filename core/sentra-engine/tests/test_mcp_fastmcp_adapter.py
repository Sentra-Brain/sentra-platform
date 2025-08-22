# import pytest
# from unittest.mock import AsyncMock
# from sentra_engine.adapters.mcp_fastmcp import MCPProtocolAdapter
# from sentra_engine.core.models import ToolSchema, ToolResult

# TODO: adapt these tests to final implementation, once it works!


# @pytest.mark.asyncio
# async def test_list_tools():
#     # Mock the RPC client
#     adapter = MCPProtocolAdapter(base_url="http://mocked-url")
#     adapter.list_tools = AsyncMock(
#         return_value=[
#             {
#                 "name": "echo",
#                 "description": "Echo tool",
#                 "inputSchema": {
#                     "type": "object",
#                     "properties": {"text": {"type": "string"}},
#                     "required": ["text"],
#                 },
#             }
#         ]
#     )

#     tools = await adapter.list_tools()
#     assert tools == [
#         ToolSchema(
#             name="echo",
#             parameters={
#                 "type": "object",
#                 "properties": {"text": {"type": "string"}},
#                 "required": ["text"],
#             },
#             title=None,
#             description="Echo tool",
#         )
#     ]


# @pytest.mark.asyncio
# async def test_call_tool():
#     # Mock the RPC client
#     adapter = MCPProtocolAdapter(base_url="http://mocked-url")
#     adapter.call_tool = AsyncMock(
#         return_value={"ok": True, "content": "pong"}
#     )

#     result = await adapter.call_tool("echo", {"text": "ping"})
#     assert result.ok is True
#     assert result.content == "pong"

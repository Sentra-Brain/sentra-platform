import pytest
import pytest_asyncio
import respx
from httpx import Response
from sentra_engine.adapters.mcp_fastmcp import MCPProtocolAdapter
from sentra_engine.core.models import ToolSchema


@pytest_asyncio.fixture
async def mock_mcp_server():
    with respx.mock as mock:
        yield mock


@pytest.mark.asyncio
async def test_list_tools(mock_mcp_server):
    adapter = MCPProtocolAdapter(base_url="http://mock-mcp")
    mock_mcp_server.post("http://mock-mcp/tools/list").mock(
        return_value=Response(
            200,
            json={
                "tools": [
                    {
                        "name": "echo",
                        "description": "Echo tool",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"text": {"type": "string"}},
                            "required": ["text"],
                        },
                    }
                ]
            },
        )
    )
    tools = await adapter.list_tools()
    assert tools == [
        ToolSchema(
            name="echo",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
            title=None,
            description="Echo tool",
        )
    ]


@pytest.mark.asyncio
async def test_call_tool(mock_mcp_server):
    adapter = MCPProtocolAdapter(base_url="http://mock-mcp")
    mock_mcp_server.post("http://mock-mcp/tools/call").mock(
        return_value=Response(200, json={"content": [{"type": "text", "text": "pong"}]})
    )
    result = await adapter.call_tool("echo", {"text": "ping"})
    assert result.ok is True
    assert result.content == "pong"

import pytest
import pytest_asyncio
import respx
from httpx import Response
from sentra_engine.adapters.llm.llama_server import LlamaServerAdapter
from sentra_engine.adapters.llm.vllm import VLLMAdapter
from sentra_engine.core.models import PromptContext, DeltaEvent

@pytest_asyncio.fixture
async def mock_llama_server():
    with respx.mock as mock:
        yield mock

@pytest_asyncio.fixture
async def mock_vllm_server():
    with respx.mock as mock:
        yield mock

@pytest.mark.asyncio
async def test_llama_server_streaming(mock_llama_server):
    adapter = LlamaServerAdapter(base_url="http://mock-llama", model="test-model")

    mock_llama_server.post("http://mock-llama/v1/chat/completions").mock(
        return_value=Response(
            200,
            content="""
data: {"choices": [{"delta": {"content": "Hello"}}]}
data: {"choices": [{"delta": {"content": " world"}}]}
data: [DONE]
""",
        )
    )

    prompt_context = PromptContext(messages=[{"role": "user", "content": "Say hello"}])
    events = [event async for event in adapter.chat_stream(prompt_context)]

    assert events == [
        DeltaEvent(type="message_delta", content="Hello"),
        DeltaEvent(type="message_delta", content=" world"),
    ]

@pytest.mark.asyncio
async def test_vllm_streaming(mock_vllm_server):
    adapter = VLLMAdapter(base_url="http://mock-vllm", model="test-model")

    mock_vllm_server.post("http://mock-vllm/v1/chat/completions").mock(
        return_value=Response(
            200,
            content="""
data: {"choices": [{"delta": {"content": "Hi"}}]}
data: {"choices": [{"delta": {"content": " there"}}]}
data: [DONE]
""",
        )
    )

    prompt_context = PromptContext(messages=[{"role": "user", "content": "Say hi"}])
    events = [event async for event in adapter.chat_stream(prompt_context)]

    assert events == [
        DeltaEvent(type="message_delta", content="Hi"),
        DeltaEvent(type="message_delta", content=" there"),
    ]

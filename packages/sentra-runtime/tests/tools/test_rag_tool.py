# import pytest

# from sentra.runtime.tools.rag_tool import RagTool, RagChunk
# from sentra.runtime.config import settings


# @pytest.mark.anyio("asyncio")
# async def test_dummy_retrieve_returns_chunks(monkeypatch) -> None:
#     monkeypatch.setattr(settings, "use_dummy", True)
#     tool = RagTool()
#     chunks = await tool.retrieve(
#         "hello", source_ids=["s1", "s2"], document_ids=["d1"], top_k=3
#     )
#     assert len(chunks) == 3
#     assert all(isinstance(c, RagChunk) for c in chunks)
#     assert all("hello" in c.content for c in chunks)


# @pytest.mark.anyio("asyncio")
# async def test_retrieve_handles_http_failure(monkeypatch) -> None:
#     monkeypatch.setattr(settings, "use_dummy", False)

#     class FailingClient:
#         async def __aenter__(self):
#             return self

#         async def __aexit__(self, *excinfo):
#             return False

#         async def post(self, *args, **kwargs):  # pragma: no cover - network stub
#             raise RuntimeError("boom")

#     monkeypatch.setattr("sentra.runtime.tools.rag_tool.httpx.AsyncClient", FailingClient)

#     tool = RagTool()
#     chunks = await tool.retrieve("hello")
#     assert chunks == []

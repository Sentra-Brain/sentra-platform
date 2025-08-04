# import pytest
# from httpx import AsyncClient
# from fastapi import status

# from sentra_brain_api.main import app


# @pytest.mark.asyncio
# async def test_list_knowledge_sources(authenticated_client: AsyncClient):
#     response = await authenticated_client.get("/knowledge")
#     assert response.status_code == status.HTTP_200_OK
#     assert "sources" in response.json()


# @pytest.mark.asyncio
# async def test_create_knowledge_source(admin_client: AsyncClient):
#     response = await admin_client.post(
#         "/knowledge",
#         json={"display_name": "My Source", "visibility": "private", "description": "For testing"}
#     )
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json()["display_name"] == "My Source"


# @pytest.mark.asyncio
# async def test_get_knowledge_source(authenticated_client: AsyncClient, example_source_id: str):
#     response = await authenticated_client.get(f"/knowledge/{example_source_id}")
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json()["id"] == example_source_id


# @pytest.mark.asyncio
# async def test_patch_knowledge_source_status(admin_client: AsyncClient, example_source_id: str):
#     response = await admin_client.patch(f"/knowledge/{example_source_id}?enabled=false")
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json()["enabled"] is False


# @pytest.mark.asyncio
# async def test_delete_knowledge_source(admin_client: AsyncClient, example_source_id: str):
#     response = await admin_client.delete(f"/knowledge/{example_source_id}")
#     assert response.status_code == status.HTTP_200_OK

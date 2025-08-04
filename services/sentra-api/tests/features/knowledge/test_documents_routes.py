# import pytest
# from httpx import AsyncClient
# from fastapi import status

# from sentra_core.domain.entities.user_entity import UserEntity
# from sentra_brain_api.main import app


# @pytest.mark.asyncio
# async def test_list_all_documents(authenticated_client: AsyncClient):
#     response = await authenticated_client.get("/knowledge/documents")
#     assert response.status_code == status.HTTP_200_OK
#     assert "documents" in response.json()


# @pytest.mark.asyncio
# async def test_upload_document_to_source(authenticated_client: AsyncClient, example_source_id: str):
#     file_content = b"Sample document content"
#     response = await authenticated_client.post(
#         f"/knowledge/sources/{example_source_id}/documents",
#         files={"file": ("example.txt", file_content, "text/plain")},
#         data={"display_name": "Example Doc", "description": "Test desc"}
#     )
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     assert data["display_name"] == "Example Doc"


# @pytest.mark.asyncio
# async def test_get_document_by_id(authenticated_client: AsyncClient, example_document_id: str):
#     response = await authenticated_client.get(f"/knowledge/documents/{example_document_id}")
#     assert response.status_code == status.HTTP_200_OK
#     assert "id" in response.json()


# @pytest.mark.asyncio
# async def test_patch_document(authenticated_client: AsyncClient, example_document_id: str):
#     response = await authenticated_client.patch(
#         f"/knowledge/documents/{example_document_id}",
#         json={"display_name": "Updated name", "description": "Updated desc"}
#     )
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     assert data["display_name"] == "Updated name"


# @pytest.mark.asyncio
# async def test_reindex_document(authenticated_client: AsyncClient, example_document_id: str):
#     response = await authenticated_client.post(f"/knowledge/documents/{example_document_id}/reindex")
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json()["id"] == example_document_id


# @pytest.mark.asyncio
# async def test_delete_document(authenticated_client: AsyncClient, example_document_id: str):
#     response = await authenticated_client.delete(f"/knowledge/documents/{example_document_id}")
#     assert response.status_code == status.HTTP_200_OK

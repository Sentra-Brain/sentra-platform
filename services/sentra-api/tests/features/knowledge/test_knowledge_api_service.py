# TODO: Figure out how to properly test this class
# becuase it interacts with the file system, multiple repositories and services.
# These tests fail during the CI pipeline due to file system access issues.

#
# import pytest
# from unittest.mock import Mock, patch, AsyncMock
# from fastapi import UploadFile, HTTPException
# from io import BytesIO
# from uuid import UUID
# from sentra_brain_api.features.knowledge.api_service import KnowledgeApiService
# from sentra_brain_api.features.knowledge.schemas import CreateKnowledgeSourceRequest, DocumentUploadRequest
# from sentra_shared.domain.entities.knowledge_source_entity import KnowledgeSourceEntity
# from sentra_shared.domain.entities.document_entity import DocumentEntity
# from sentra_shared.domain.enums.knowledge import KnowledgeSourceType, KnowledgeSourceVisibility
# from sentra_shared.domain.constants.file_types import ALLOWED_FILE_TYPES

# @pytest.fixture
# def mock_knowledge_repo():
#     return Mock()

# @pytest.fixture
# def mock_document_repo():
#     return Mock()

# @pytest.fixture
# def mock_indexing_publisher():
#     return Mock()

# @pytest.fixture
# def object_to_test(mock_knowledge_repo, mock_document_repo, mock_indexing_publisher):
#     return KnowledgeApiService(
#         knowledge_repo=mock_knowledge_repo,
#         document_repo=mock_document_repo,
#         indexing_publisher=mock_indexing_publisher
#     )

# @pytest.fixture
# def mock_user():
#     user = Mock()
#     user.id = "user-id"
#     user.username = "testuser"
#     return user

# def test_create_knowledge_source_valid(object_to_test, mock_knowledge_repo, mock_user):
#     request = CreateKnowledgeSourceRequest(
#         name="Source",
#         type=KnowledgeSourceType.FOLDER,
#         path="/mnt/data/source",
#         description="desc"
#     )
#     expected_entity = Mock()
#     expected_entity.id = UUID("123e4567-e89b-12d3-a456-426614174000")
#     object_to_test.knowledge_svc.create_knowledge_source = Mock(return_value=expected_entity)

#     result = object_to_test.create_knowledge_source(request, mock_user)

#     assert result == expected_entity
#     object_to_test.knowledge_svc.create_knowledge_source.assert_called_once()


# def test_create_folder_knowledge_source_raises_if_path_outside_mount(object_to_test, mock_user):
#     # Arrange
#     request = CreateKnowledgeSourceRequest(
#         name="Source",
#         type=KnowledgeSourceType.FOLDER,
#         path="/etc/passwd",
#         description="desc"
#     )
#     # Act & Assert
#     with pytest.raises(HTTPException) as exc:
#         object_to_test.create_knowledge_source(request, mock_user)
#     assert exc.value.status_code == 400
#     assert "must be under" in str(exc.value.detail)

# def test_create_folder_knowledge_source_raises_if_path_missing(object_to_test, mock_user):
#     # Arrange
#     request = CreateKnowledgeSourceRequest(
#         name="Source",
#         type=KnowledgeSourceType.FOLDER,
#         description="desc"
#     )
#     # Act & Assert
#     with pytest.raises(HTTPException) as exc:
#         object_to_test.create_knowledge_source(request, mock_user)
#     assert exc.value.status_code == 400
#     assert "Path is required" in str(exc.value.detail)


# def test_list_knowledge_sources(object_to_test, mock_knowledge_repo, mock_user):
#     mock_sources = [Mock(), Mock()]
#     mock_sources[0].id = UUID("123e4567-e89b-12d3-a456-426614174000")
#     mock_sources[1].id = UUID("123e4567-e89b-12d3-a456-426614174001")
#     mock_knowledge_repo.list_by_user.return_value = mock_sources
#     mock_knowledge_repo.count_by_user.return_value = 2

#     sources, total = object_to_test.list_knowledge_sources(mock_user, limit=10, offset=0)

#     assert sources == mock_sources
#     assert total == 2
#     mock_knowledge_repo.list_by_user.assert_called_once_with(mock_user.id, 10, 0)
#     mock_knowledge_repo.count_by_user.assert_called_once_with(mock_user.id)

# def test_list_documents(object_to_test, mock_document_repo, mock_user):
#     mock_docs = [Mock(), Mock()]
#     mock_docs[0].id = UUID("123e4567-e89b-12d3-a456-426614174002")
#     mock_docs[1].id = UUID("123e4567-e89b-12d3-a456-426614174003")
#     mock_document_repo.list_by_user_or_source.return_value = mock_docs
#     mock_document_repo.count_by_user_or_source.return_value = 2

#     docs, total = object_to_test.list_documents(mock_user, source_id=None, limit=10, offset=0)

#     assert docs == mock_docs
#     assert total == 2
#     mock_document_repo.list_by_user_or_source.assert_called_once_with(mock_user.id, None, 10, 0)
#     mock_document_repo.count_by_user_or_source.assert_called_once_with(mock_user.id, None)

# def test_update_knowledge_source_status(object_to_test):
#     source_id = "123e4567-e89b-12d3-a456-426614174000"
#     enabled = True
#     expected_entity = Mock()
#     expected_entity.id = UUID(source_id)
#     object_to_test.knowledge_svc.update_status = Mock(return_value=expected_entity)

#     result = object_to_test.update_knowledge_source_status(source_id, enabled)

#     assert result == expected_entity
#     object_to_test.knowledge_svc.update_status.assert_called_once_with(UUID(source_id), enabled)

# def test_remove_document(object_to_test, mock_document_repo, mock_user):
#     document_id = "123e4567-e89b-12d3-a456-426614174002"
#     doc = Mock()
#     doc.id = UUID(document_id)
#     object_to_test.document_svc.mark_for_removal = Mock(return_value=doc)

#     result = object_to_test.remove_document(document_id, mock_user)

#     assert result == doc
#     object_to_test.document_svc.mark_for_removal.assert_called_once_with(UUID(document_id), mock_user.id)
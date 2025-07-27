# tests/features/knowledge/test_knowledge_service.py

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from fastapi import UploadFile, HTTPException
from io import BytesIO

from sentra_shared.domain.entities.user_entity import UserEntity
from sentra_shared.domain.entities.knowledge_source_entity import KnowledgeSourceEntity, KnowledgeSourceType, KnowledgeSourceVisibility
from sentra_shared.domain.entities.document_entity import DocumentEntity, DocumentFileType
from sentra_shared.domain.repositories.knowledge_repository import KnowledgeRepository
from sentra_brain_api.features.knowledge.service import KnowledgeService
from sentra_brain_api.features.knowledge.models import CreateKnowledgeSourceRequest, DocumentUploadRequest
from sentra_shared.infra.amqp.publisher import RabbitMQPublisher


class TestKnowledgeService:
    @pytest.fixture
    def mock_repository(self):
        return Mock(spec=KnowledgeRepository)

    @pytest.fixture
    def mock_rabbitmq_publisher(self):
        return Mock(spec=RabbitMQPublisher)

    @pytest.fixture
    def service(self, mock_repository, mock_rabbitmq_publisher):
        return KnowledgeService(mock_repository, mock_rabbitmq_publisher)

    @pytest.fixture
    def mock_user(self):
        user = Mock(spec=UserEntity)
        user.id = "test-user-id"
        user.username = "testuser"
        return user

    @pytest.fixture
    def temp_mount_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_create_knowledge_source_folder_type_valid_path(self, service, mock_user, temp_mount_path):
        """Test creating a folder-type knowledge source with valid path"""
        with patch.object(service, '_get_settings') as mock_settings:
            mock_settings.return_value.knowledge_mount_path = temp_mount_path
            
            # Create a test subfolder
            test_folder = Path(temp_mount_path) / "test_folder"
            test_folder.mkdir()
            
            request = CreateKnowledgeSourceRequest(
                name="Test Folder Source",
                type=KnowledgeSourceType.FOLDER,
                path=str(test_folder),
                description="Test description"
            )
            
            # Mock repository behavior
            expected_source = KnowledgeSourceEntity(
                name=request.name,
                type=request.type,
                path=request.path,
                description=request.description,
                created_by=mock_user.id,
                visibility=request.visibility,
                auto_index=request.auto_index
            )
            service.repository.create_knowledge_source.return_value = expected_source
            
            # Execute
            result = service.create_knowledge_source(request, mock_user)
            
            # Assert
            assert result == expected_source
            service.repository.create_knowledge_source.assert_called_once()

    def test_create_knowledge_source_folder_type_invalid_path(self, service, mock_user, temp_mount_path):
        """Test creating a folder-type knowledge source with path outside mount"""
        with patch.object(service, '_get_settings') as mock_settings:
            mock_settings.return_value.knowledge_mount_path = temp_mount_path
            
            request = CreateKnowledgeSourceRequest(
                name="Test Folder Source",
                type=KnowledgeSourceType.FOLDER,
                path="/etc/passwd",  # Outside mount path
                description="Test description"
            )
            
            # Execute & Assert
            with pytest.raises(HTTPException) as exc_info:
                service.create_knowledge_source(request, mock_user)
            
            assert exc_info.value.status_code == 400
            assert "must be under" in str(exc_info.value.detail)

    def test_create_knowledge_source_folder_type_no_path(self, service, mock_user):
        """Test creating a folder-type knowledge source without path"""
        request = CreateKnowledgeSourceRequest(
            name="Test Folder Source",
            type=KnowledgeSourceType.FOLDER,
            # path is None
            description="Test description"
        )
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_knowledge_source(request, mock_user)
        
        assert exc_info.value.status_code == 400
        assert "Path is required" in str(exc_info.value.detail)

    def test_upload_document_valid_file(self, service, mock_user, temp_mount_path):
        """Test uploading a valid document"""
        with patch.object(service, '_get_settings') as mock_settings:
            mock_settings.return_value.knowledge_mount_path = temp_mount_path
            
            # Create mock file
            file_content = b"Test PDF content"
            file = UploadFile(
                filename="test.pdf",
                file=BytesIO(file_content)
            )
            
            request = DocumentUploadRequest(
                display_name="Test Document",
                description="Test description"
            )
            
            # Mock existing upload source
            upload_source = KnowledgeSourceEntity(
                name=f"{mock_user.username}'s Uploads",
                type=KnowledgeSourceType.UPLOAD,
                created_by=mock_user.id
            )
            upload_source.id = "upload-source-id"
            
            service.repository.list_knowledge_sources.return_value = [upload_source]
            
            # Mock document creation
            expected_document = DocumentEntity(
                filename=file.filename,
                display_name=request.display_name,
                description=request.description,
                filetype=DocumentFileType.PDF,
                uploaded_by=mock_user.id,
                knowledge_source_id=upload_source.id
            )
            expected_document.id = "document-id"
            service.repository.create_document.return_value = expected_document
            
            # Mock RabbitMQ publisher context manager
            service.rabbitmq_publisher.__enter__ = Mock(return_value=service.rabbitmq_publisher)
            service.rabbitmq_publisher.__exit__ = Mock(return_value=None)
            
            # Execute
            result = service.upload_document(file, request, mock_user)
            
            # Assert
            assert result == expected_document
            service.repository.create_document.assert_called_once()
            service.rabbitmq_publisher.__enter__.assert_called_once()
            service.rabbitmq_publisher.publish_indexation_job.assert_called_once()

    def test_upload_document_invalid_file_type(self, service, mock_user):
        """Test uploading a document with unsupported file type"""
        # Create mock file with unsupported extension
        file_content = b"Test content"
        file = UploadFile(
            filename="test.xyz",  # Unsupported extension
            file=BytesIO(file_content)
        )
        
        request = DocumentUploadRequest(
            display_name="Test Document"
        )
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.upload_document(file, request, mock_user)
        
        assert exc_info.value.status_code == 400
        assert "Unsupported file type" in str(exc_info.value.detail)

    def test_upload_document_creates_upload_source_if_not_exists(self, service, mock_user, temp_mount_path):
        """Test that upload source is created if it doesn't exist for user"""
        with patch.object(service, '_get_settings') as mock_settings:
            mock_settings.return_value.knowledge_mount_path = temp_mount_path
            
            file_content = b"Test content"
            file = UploadFile(
                filename="test.txt",
                file=BytesIO(file_content)
            )
            
            request = DocumentUploadRequest(
                display_name="Test Document"
            )
            
            # Mock no existing upload sources
            service.repository.list_knowledge_sources.return_value = []
            
            # Mock upload source creation
            new_upload_source = KnowledgeSourceEntity(
                name=f"{mock_user.username}'s Uploads",
                type=KnowledgeSourceType.UPLOAD,
                created_by=mock_user.id
            )
            new_upload_source.id = "new-upload-source-id"
            service.repository.create_knowledge_source.return_value = new_upload_source
            
            # Mock document creation
            expected_document = DocumentEntity(
                filename=file.filename,
                display_name=request.display_name,
                filetype=DocumentFileType.TXT,
                uploaded_by=mock_user.id,
                knowledge_source_id=new_upload_source.id
            )
            service.repository.create_document.return_value = expected_document
            
            # Mock RabbitMQ publisher context manager
            service.rabbitmq_publisher.__enter__ = Mock(return_value=service.rabbitmq_publisher)
            service.rabbitmq_publisher.__exit__ = Mock(return_value=None)
            
            # Execute
            result = service.upload_document(file, request, mock_user)
            
            # Assert
            service.repository.create_knowledge_source.assert_called_once()
            service.repository.create_document.assert_called_once()

    def test_list_knowledge_sources(self, service, mock_user):
        """Test listing knowledge sources"""
        mock_sources = [
            Mock(spec=KnowledgeSourceEntity),
            Mock(spec=KnowledgeSourceEntity)
        ]
        
        service.repository.list_knowledge_sources.return_value = mock_sources
        service.repository.get_knowledge_sources_count.return_value = 2
        
        # Execute
        sources, total = service.list_knowledge_sources(mock_user, limit=10, offset=0)
        
        # Assert
        assert sources == mock_sources
        assert total == 2
        service.repository.list_knowledge_sources.assert_called_once_with(
            created_by=mock_user.id, limit=10, offset=0
        )
        service.repository.get_knowledge_sources_count.assert_called_once_with(
            created_by=mock_user.id
        )

    def test_list_documents(self, service, mock_user):
        """Test listing documents"""
        mock_documents = [
            Mock(spec=DocumentEntity),
            Mock(spec=DocumentEntity)
        ]
        
        service.repository.list_documents.return_value = mock_documents
        service.repository.get_documents_count.return_value = 2
        
        # Execute
        documents, total = service.list_documents(mock_user, limit=10, offset=0)
        
        # Assert
        assert documents == mock_documents
        assert total == 2
        service.repository.list_documents.assert_called_once_with(
            uploaded_by=mock_user.id, knowledge_source_id=None, limit=10, offset=0
        )
        service.repository.get_documents_count.assert_called_once_with(
            uploaded_by=mock_user.id, knowledge_source_id=None
        )
"""
Integration test for the document upload and indexing workflow.

This test validates the end-to-end flow from file upload through to message
processing, ensuring the new FileStorageService and IndexingJobPublisher work correctly.
"""

import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from io import BytesIO

from sentra_core.domain.services.file_storage import FileStorageService
from sentra_core.domain.services.indexing_publisher import IndexingJobPublisher, create_indexing_job


class TestEndToEndWorkflow:
    """Test the complete document processing workflow."""
    
    @pytest.fixture
    def temp_mount_path(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_complete_upload_workflow(self, temp_mount_path):
        """Test the complete workflow from upload to indexing job creation."""
        # 1. Setup file storage service
        file_storage = FileStorageService(temp_mount_path)
        
        # 2. Create file content
        file_content = b"This is a test PDF document with some content for indexing."
        file_obj = BytesIO(file_content)
        
        user_id = "test-user-123"
        filename = "test_document.pdf"
        
        # 3. Save the file using FileStorageService
        absolute_path, relative_path = file_storage.save_file(file_obj, filename, user_id)
        
        # 4. Verify file was saved correctly
        assert absolute_path.exists()
        assert absolute_path.read_bytes() == file_content
        assert absolute_path.name == "test_document.pdf"  # Original filename preserved
        assert relative_path == f"uploads/{user_id}/test_document.pdf"
        
        # 5. Create indexing job
        job = create_indexing_job(
            document_id="doc-123",
            document_path=relative_path,
            knowledge_source_id="source-456",
            filename="test_document.pdf",
            uploaded_by=user_id
        )
        
        # 6. Verify job structure
        expected_job = {
            "document_id": "doc-123",
            "document_path": relative_path,
            "knowledge_source_id": "source-456",
            "action": "index_document",
            "filename": "test_document.pdf",
            "uploaded_by": user_id
        }
        assert job == expected_job
        
        # 7. Test path resolution in worker context
        resolved_path = file_storage.resolve_document_path(relative_path)
        assert resolved_path == absolute_path
        assert file_storage.validate_file_exists(relative_path)
        
        # 8. Get file info
        info = file_storage.get_file_info(relative_path)
        assert info is not None
        assert info["filename"] == "test_document.pdf"
        assert info["size"] == len(file_content)
    
    def test_filename_collision_handling(self, temp_mount_path):
        """Test that filename collisions are handled correctly."""
        file_storage = FileStorageService(temp_mount_path)
        user_id = "test-user-collision"
        
        # Create first file
        file_content_1 = b"First file content"
        file_obj_1 = BytesIO(file_content_1)
        filename_1 = "document.pdf"
        
        path_1, rel_path_1 = file_storage.save_file(file_obj_1, filename_1, user_id)
        
        # Create second file with same name
        file_content_2 = b"Second file content"
        file_obj_2 = BytesIO(file_content_2)
        filename_2 = "document.pdf"
        
        path_2, rel_path_2 = file_storage.save_file(file_obj_2, filename_2, user_id)
        
        # Verify collision was handled
        assert path_1.name == "document.pdf"
        assert path_2.name == "document_1.pdf"
        assert path_1.read_bytes() == file_content_1
        assert path_2.read_bytes() == file_content_2
        assert rel_path_1 != rel_path_2
    
    def test_indexing_job_publisher_message_format(self):
        """Test that the IndexingJobPublisher creates correctly formatted messages."""
        publisher = IndexingJobPublisher()

        # Manually mock connect() and assign mock channel
        with patch.object(publisher, 'connect'):
            mock_channel = Mock()
            publisher.channel = mock_channel  # This line fixes the test

            success = publisher.publish_indexing_job(
                document_id="test-doc-id",
                document_path="uploads/user123/doc.pdf",
                knowledge_source_id="source-id",
                filename="doc.pdf",
                uploaded_by="user123"
            )

            # Assertions
            assert success is True
            mock_channel.basic_publish.assert_called_once()

            # Check message body
            call_args = mock_channel.basic_publish.call_args
            message_body = call_args.kwargs["body"]
            message_dict = json.loads(message_body)

            assert message_dict == {
                "document_id": "test-doc-id",
                "document_path": "uploads/user123/doc.pdf",
                "knowledge_source_id": "source-id",
                "action": "index_document",
                "filename": "doc.pdf",
                "uploaded_by": "user123"
            }

    
    def test_path_security_validation(self, temp_mount_path):
        """Test that path traversal attempts are prevented."""
        file_storage = FileStorageService(temp_mount_path)
        
        # Test path traversal prevention
        with pytest.raises(ValueError, match="resolves outside mount point"):
            file_storage.resolve_document_path("../../../etc/passwd")
        
        with pytest.raises(ValueError, match="resolves outside mount point"):
            file_storage.resolve_document_path("uploads/../../../sensitive_file")
    
    def test_filename_sanitization_security(self, temp_mount_path):
        """Test that dangerous filenames are properly sanitized."""
        file_storage = FileStorageService(temp_mount_path)
        
        # Test various problematic filenames
        test_cases = [
            ("../../../etc/passwd", "passwd"),
            ("file with spaces.pdf", "file_with_spaces.pdf"),
            ("file<>:\"|?*.txt", "file_______.txt"),  # Each special char becomes one _
            (".hidden_file", "file_.hidden_file"),
            ("", "unnamed_file"),
            ("normal_file.pdf", "normal_file.pdf")  # Should remain unchanged
        ]
        
        for dangerous_name, expected_safe_name in test_cases:
            safe_name = file_storage.sanitize_filename(dangerous_name)
            assert safe_name == expected_safe_name
            # Verify the safe name doesn't contain path separators
            assert "/" not in safe_name
            assert "\\" not in safe_name
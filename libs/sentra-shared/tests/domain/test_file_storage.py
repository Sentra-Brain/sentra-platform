"""
Tests for FileStorageService.

These tests validate the core functionality of the shared file storage service,
ensuring consistent file handling with original filenames.
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from io import BytesIO
from fastapi import UploadFile

from sentra_shared.domain.services.file_storage import FileStorageService


class TestFileStorageService:
    
    @pytest.fixture
    def temp_mount_path(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def file_storage(self, temp_mount_path):
        """Create FileStorageService instance with temp mount path."""
        return FileStorageService(temp_mount_path)
    
    def test_sanitize_filename_basic(self, file_storage):
        """Test basic filename sanitization."""
        # Normal filename
        assert file_storage.sanitize_filename("document.pdf") == "document.pdf"
        
        # Filename with spaces and special chars
        assert file_storage.sanitize_filename("my document (1).pdf") == "my_document__1_.pdf"
        
        # Filename with path traversal attempt
        assert file_storage.sanitize_filename("../../../etc/passwd") == "passwd"
        
        # Hidden file
        assert file_storage.sanitize_filename(".hidden") == "file_.hidden"
        
        # Empty filename
        assert file_storage.sanitize_filename("") == "unnamed_file"
        assert file_storage.sanitize_filename(None) == "unnamed_file"
    
    def test_create_user_upload_directory(self, file_storage, temp_mount_path):
        """Test user upload directory creation."""
        user_id = "test-user-123"
        upload_dir = file_storage.create_user_upload_directory(user_id)
        
        expected_path = Path(temp_mount_path) / "uploads" / user_id
        assert upload_dir == expected_path
        assert upload_dir.exists()
        assert upload_dir.is_dir()
    
    def test_handle_filename_collision(self, file_storage, temp_mount_path):
        """Test filename collision handling."""
        # Create a file
        test_dir = Path(temp_mount_path) / "test"
        test_dir.mkdir()
        
        original_file = test_dir / "document.pdf"
        original_file.write_text("content")
        
        # Test collision handling
        result_path = file_storage.handle_filename_collision(original_file)
        assert result_path == test_dir / "document_1.pdf"
        
        # Create the collision file and test again
        result_path.write_text("content")
        result_path2 = file_storage.handle_filename_collision(original_file)
        assert result_path2 == test_dir / "document_2.pdf"
    
    def test_save_uploaded_file(self, file_storage, temp_mount_path):
        """Test saving an uploaded file."""
        # Create mock uploaded file
        file_content = b"Test PDF content"
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test_document.pdf"
        mock_file.file = BytesIO(file_content)
        
        user_id = "test-user-456"
        
        # Save the file
        absolute_path, relative_path = file_storage.save_uploaded_file(mock_file, user_id)
        
        # Verify results
        expected_relative = f"uploads/{user_id}/test_document.pdf"
        assert relative_path == expected_relative
        assert absolute_path.is_file()
        assert absolute_path.read_bytes() == file_content
        
        # Verify file is in correct location
        expected_absolute = Path(temp_mount_path) / expected_relative
        assert absolute_path == expected_absolute
    
    def test_save_uploaded_file_with_collision(self, file_storage, temp_mount_path):
        """Test saving uploaded file with filename collision."""
        # Create existing file
        user_id = "test-user-789"
        upload_dir = file_storage.create_user_upload_directory(user_id)
        existing_file = upload_dir / "document.pdf"
        existing_file.write_text("existing content")
        
        # Create new file with same name
        file_content = b"New content"
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "document.pdf"
        mock_file.file = BytesIO(file_content)
        
        # Save the file
        absolute_path, relative_path = file_storage.save_uploaded_file(mock_file, user_id)
        
        # Should have collision handling
        assert "document_1.pdf" in relative_path
        assert absolute_path.read_bytes() == file_content
        assert existing_file.read_text() == "existing content"  # Original unchanged
    
    def test_resolve_document_path(self, file_storage, temp_mount_path):
        """Test document path resolution."""
        # Create a test file
        test_file = Path(temp_mount_path) / "uploads" / "user123" / "doc.pdf"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("content")
        
        # Test valid path resolution
        relative_path = "uploads/user123/doc.pdf"
        resolved = file_storage.resolve_document_path(relative_path)
        assert resolved == test_file
        
        # Test path traversal prevention
        with pytest.raises(ValueError, match="resolves outside mount point"):
            file_storage.resolve_document_path("../../../etc/passwd")
    
    def test_validate_file_exists(self, file_storage, temp_mount_path):
        """Test file existence validation."""
        # Create a test file
        test_file = Path(temp_mount_path) / "test.txt"
        test_file.write_text("content")
        
        # Test existing file
        assert file_storage.validate_file_exists("test.txt") is True
        
        # Test non-existing file
        assert file_storage.validate_file_exists("nonexistent.txt") is False
        
        # Test directory (should return False)
        test_dir = Path(temp_mount_path) / "testdir"
        test_dir.mkdir()
        assert file_storage.validate_file_exists("testdir") is False
    
    def test_get_file_info(self, file_storage, temp_mount_path):
        """Test file information retrieval."""
        # Create a test file
        test_file = Path(temp_mount_path) / "info_test.txt"
        test_content = "test content"
        test_file.write_text(test_content)
        
        # Get file info
        info = file_storage.get_file_info("info_test.txt")
        
        assert info is not None
        assert info["filename"] == "info_test.txt"
        assert info["size"] == len(test_content)
        assert "modified" in info
        assert "absolute_path" in info
        
        # Test non-existing file
        assert file_storage.get_file_info("nonexistent.txt") is None
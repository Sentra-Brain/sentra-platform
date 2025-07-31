"""
Shared file storage service for consistent file handling across the application.

This service handles file naming, path resolution, and storage operations
using original filenames without GUID prefixes, ensuring consistent behavior
between the API producer and RAG worker consumer.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple, BinaryIO

from sentra_core.core.logging import get_logger

logger = get_logger(__name__)


class FileStorageService:
    """Centralized file storage service for knowledge documents."""
    
    def __init__(self, mount_path: str):
        """
        Initialize file storage service.
        
        Args:
            mount_path: Root mount path for knowledge files
        """
        self.mount_path = Path(mount_path)
        self.mount_path.mkdir(parents=True, exist_ok=True)
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename to prevent path traversal and ensure filesystem compatibility.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename safe for filesystem use
        """
        if not filename:
            return "unnamed_file"
        
        # Remove path components to prevent traversal
        filename = os.path.basename(filename)
        
        # Replace problematic characters
        # Keep alphanumeric, dots, hyphens, underscores
        sanitized = re.sub(r'[^\w\-_.]', '_', filename)
        
        # Ensure it doesn't start with a dot (hidden file)
        if sanitized.startswith('.'):
            sanitized = 'file_' + sanitized
        
        # Limit length to 255 characters (common filesystem limit)
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            max_name_len = 255 - len(ext)
            sanitized = name[:max_name_len] + ext
        
        return sanitized
    
    def create_user_upload_directory(self, user_id: str) -> Path:
        """
        Create and return the upload directory for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Path to user's upload directory
        """
        upload_dir = self.mount_path / "uploads" / str(user_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir
    
    def handle_filename_collision(self, file_path: Path) -> Path:
        """
        Handle filename collisions by appending a counter.
        
        Args:
            file_path: Desired file path
            
        Returns:
            Available file path (may have counter appended)
        """
        if not file_path.exists():
            return file_path
        
        # Extract parts
        stem = file_path.stem
        suffix = file_path.suffix
        parent = file_path.parent
        
        # Try incremental naming
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
            
            # Safety limit to prevent infinite loops
            if counter > 1000:
                # Fallback to timestamp-based naming
                import time
                timestamp = int(time.time())
                new_name = f"{stem}_{timestamp}{suffix}"
                return parent / new_name
    
    def save_file(self, file_content: BinaryIO, filename: str, user_id: str) -> Tuple[Path, str]:
        """
        Save file content using original filename.
        
        Args:
            file_content: File-like object with file content
            filename: Original filename
            user_id: ID of the uploading user
            
        Returns:
            Tuple of (absolute_file_path, relative_path_from_mount)
            
        Raises:
            Exception: If file saving fails
        """
        # Sanitize the original filename
        safe_filename = self.sanitize_filename(filename)
        
        # Create user directory
        upload_dir = self.create_user_upload_directory(user_id)
        
        # Handle potential filename collisions
        desired_path = upload_dir / safe_filename
        final_path = self.handle_filename_collision(desired_path)
        
        # Save the file
        try:
            with open(final_path, "wb") as buffer:
                # Reset file pointer in case it was read before
                file_content.seek(0)
                buffer.write(file_content.read())
            
            logger.info(f"File saved: {final_path}")
            
            # Calculate relative path from mount point
            relative_path = final_path.relative_to(self.mount_path)
            
            return final_path, str(relative_path)
            
        except Exception as e:
            logger.error(f"Failed to save file {safe_filename}: {e}")
            # Clean up if file was partially created
            if final_path.exists():
                try:
                    final_path.unlink()
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup partial file {final_path}: {cleanup_error}")
            raise
    
    def resolve_document_path(self, relative_path: str) -> Path:
        """
        Resolve a relative document path to absolute path.
        
        Args:
            relative_path: Path relative to mount point
            
        Returns:
            Absolute path to the document
        """
        # Ensure the path is relative to mount point
        abs_path = (self.mount_path / relative_path).resolve()
        
        # Security check: ensure resolved path is under mount point
        try:
            abs_path.relative_to(self.mount_path.resolve())
        except ValueError:
            raise ValueError(f"Path {relative_path} resolves outside mount point")
        
        return abs_path
    
    def validate_file_exists(self, relative_path: str) -> bool:
        """
        Check if a file exists at the given relative path.
        
        Args:
            relative_path: Path relative to mount point
            
        Returns:
            True if file exists and is readable, False otherwise
        """
        try:
            abs_path = self.resolve_document_path(relative_path)
            return abs_path.is_file() and os.access(abs_path, os.R_OK)
        except (ValueError, OSError):
            return False
    
    def get_file_info(self, relative_path: str) -> Optional[dict]:
        """
        Get file information for a document.
        
        Args:
            relative_path: Path relative to mount point
            
        Returns:
            Dictionary with file info or None if file doesn't exist
        """
        try:
            abs_path = self.resolve_document_path(relative_path)
            if not abs_path.is_file():
                return None
            
            stat = abs_path.stat()
            return {
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "filename": abs_path.name,
                "absolute_path": str(abs_path)
            }
        except (ValueError, OSError):
            return None
"""
Shared file storage service for consistent file handling across the application.

This service handles file naming, path resolution, and storage operations
using original filenames without GUID prefixes, ensuring consistent behavior
between the API producer and RAG worker consumer.
"""

import gzip
import hashlib
import os
import re
from pathlib import Path
from uuid import UUID
from typing import Optional, Tuple, BinaryIO

from sentra.shared.logging import get_logger

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

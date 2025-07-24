import os
from typing import List, Union
from pathlib import Path
from sentra_rag_worker.core.logging import get_logger
from sentra_rag_worker.domain.document_entity import DocumentFileType

logger = get_logger(__name__)


class DocumentExtractor:
    """Extract clean text content from various document formats."""

    def extract_content(self, filepath: str, filetype: DocumentFileType) -> str:
        """Extract text content from a document.
        
        Args:
            filepath: Path to the document file
            filetype: Type of the document
            
        Returns:
            Extracted text content as a string
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If extraction fails
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            logger.info(f"Extracting content from {filepath} (type: {filetype.value})")
            
            # For now, implement basic text extraction to avoid dependency issues
            if filetype == DocumentFileType.TXT or filetype == DocumentFileType.MD:
                return self._extract_text_file(filepath)
            elif filetype == DocumentFileType.PDF:
                return self._extract_pdf_simple(filepath)
            elif filetype == DocumentFileType.DOCX:
                return self._extract_docx_simple(filepath)
            else:
                # Fallback to text file reading
                return self._extract_text_file(filepath)
            
        except Exception as e:
            logger.error(f"Failed to extract content from {filepath}: {e}")
            raise ValueError(f"Content extraction failed: {str(e)}")

    def _extract_text_file(self, filepath: str) -> str:
        """Extract content from plain text files."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Successfully extracted {len(content)} characters from text file")
            return content.strip()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
            logger.info(f"Successfully extracted {len(content)} characters from text file (latin-1)")
            return content.strip()

    def _extract_pdf_simple(self, filepath: str) -> str:
        """Simple PDF extraction - placeholder for now."""
        # For production, this should use a working PDF library
        # For now, return a placeholder to avoid dependency issues
        logger.warning(f"PDF extraction not fully implemented for {filepath}")
        return f"[PDF content from {os.path.basename(filepath)} - extraction not implemented]"

    def _extract_docx_simple(self, filepath: str) -> str:
        """Simple DOCX extraction - placeholder for now."""
        # For production, this should use python-docx or similar
        # For now, return a placeholder to avoid dependency issues
        logger.warning(f"DOCX extraction not fully implemented for {filepath}")
        return f"[DOCX content from {os.path.basename(filepath)} - extraction not implemented]"
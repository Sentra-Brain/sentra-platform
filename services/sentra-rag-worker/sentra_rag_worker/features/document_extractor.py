import os
from typing import List, Union
from pathlib import Path
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.text import partition_text
from unstructured.partition.md import partition_md
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
            
            # Choose the appropriate partition function based on file type
            if filetype == DocumentFileType.PDF:
                elements = partition_pdf(filepath)
            elif filetype == DocumentFileType.DOCX:
                elements = partition_docx(filepath)
            elif filetype == DocumentFileType.TXT:
                elements = partition_text(filepath)
            elif filetype == DocumentFileType.MD:
                elements = partition_md(filepath)
            else:
                # Fallback to auto-detection
                elements = partition(filepath)
            
            # Extract only narrative text elements (skip tables, page numbers, etc.)
            text_content = []
            for element in elements:
                # Filter for narrative text elements
                if hasattr(element, 'category') and element.category in ['NarrativeText', 'Text']:
                    if hasattr(element, 'text') and element.text.strip():
                        text_content.append(element.text.strip())
                elif hasattr(element, 'text') and element.text.strip():
                    # Fallback for elements without category
                    text_content.append(element.text.strip())
            
            if not text_content:
                logger.warning(f"No text content extracted from {filepath}")
                return ""
            
            # Join all text content with double newlines
            extracted_text = "\n\n".join(text_content)
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters from {filepath}")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Failed to extract content from {filepath}: {e}")
            raise ValueError(f"Content extraction failed: {str(e)}")
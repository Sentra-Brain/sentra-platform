"""Base classes and interfaces for document extraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class ExtractionPayload:
    """Result of document extraction with structured metadata."""
    
    raw_text: str
    pages: Optional[int] = None
    html_blocks: Optional[List[str]] = None
    email_headers: Optional[Dict[str, str]] = None
    meta: Optional[Dict[str, Any]] = None
    
    @property
    def word_count(self) -> int:
        """Estimate word count from raw text."""
        if not self.raw_text:
            return 0
        return len(self.raw_text.split())

class DocumentExtractorBase(ABC):
    @abstractmethod
    def extract(self, filepath: str) -> ExtractionPayload:
        """
        Extracts the contents of a document from the given file path and returns a structured payload.
        Args:
            filepath (str): The path to the document file to be extracted.
        Returns:
            ExtractionPayload: An object containing the raw text, metadata, page count, HTML blocks, email headers, and other relevant information extracted from the document.
        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the file format is unsupported or extraction fails.
            Exception: For other unexpected errors during extraction.
        Implementers should ensure that all relevant metadata is captured and that the extraction process is robust to common file errors.
        """

    @abstractmethod
    def extract_markdown(self, filepath: str) -> str:
        """
        Returns Markdown string representation of the document.
        
        Args:
            filepath (str): The path to the document file to be converted to Markdown.
        
        Returns:
            str: The Markdown representation of the document.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the file format is unsupported or conversion fails.
            Exception: For other unexpected errors during conversion.
        """
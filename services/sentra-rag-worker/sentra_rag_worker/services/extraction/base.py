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
    """Abstract base class for document extractors."""
    
    @abstractmethod
    def extract(self, filepath: str) -> ExtractionPayload:
        """Extract content and metadata from a document.
        
        Args:
            filepath: Path to the document file
            
        Returns:
            ExtractionPayload with extracted content and metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If extraction fails
        """
        pass
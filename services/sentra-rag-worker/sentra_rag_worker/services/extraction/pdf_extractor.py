"""PDF document extractor using PyMuPDF."""

import os
import pymupdf
from sentra_core.core.logging import get_logger
from .base import DocumentExtractorBase, ExtractionPayload

logger = get_logger(__name__)


class PdfExtractor(DocumentExtractorBase):
    """Extract text and metadata from PDF documents."""
    
    def extract(self, filepath: str) -> ExtractionPayload:
        """Extract content from PDF file.
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            ExtractionPayload with text, page count, and metadata
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            logger.info(f"Extracting PDF content from {filepath}")
            
            with pymupdf.open(filepath) as doc:
                # Extract text from all pages with page separators
                pages_text = []
                for page in doc:
                    page_text = page.get_text()
                    pages_text.append(page_text)
                
                # Join pages with form feed character (will be converted to markdown separator later)
                raw_text = chr(12).join(pages_text)
                
                # Extract metadata
                metadata = doc.metadata or {}
                
                # Get document properties
                page_count = len(doc)
                
                logger.info(f"Successfully extracted {len(raw_text)} characters from {page_count} pages")
                
                return ExtractionPayload(
                    raw_text=raw_text.strip(),
                    pages=page_count,
                    meta={
                        'title': metadata.get('title'),
                        'subject': metadata.get('subject'), 
                        'author': metadata.get('author'),
                        'creator': metadata.get('creator'),
                        'producer': metadata.get('producer'),
                        'creation_date': metadata.get('creationDate'),
                        'modification_date': metadata.get('modDate'),
                        'keywords': metadata.get('keywords')
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to extract PDF content from {filepath}: {e}")
            raise ValueError(f"PDF extraction failed: {str(e)}")
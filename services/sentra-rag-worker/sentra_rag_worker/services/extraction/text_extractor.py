"""Text and Markdown document extractor."""

import os
import chardet
from sentra_core.core.logging import get_logger
from .base import DocumentExtractorBase, ExtractionPayload

logger = get_logger(__name__)


class TextExtractor(DocumentExtractorBase):
    """Extract text from TXT and MD documents."""
    
    def extract(self, filepath: str) -> ExtractionPayload:
        """Extract content from text file.
        
        Args:
            filepath: Path to the text file
            
        Returns:
            ExtractionPayload with extracted text
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            logger.info(f"Extracting text content from {filepath}")
            
            # Detect encoding
            with open(filepath, 'rb') as f:
                raw = f.read()
                result = chardet.detect(raw)
                encoding = result['encoding'] or 'utf-8'
            
            # Read content with detected encoding
            with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                raw_text = f.read()
            
            # Determine if this is markdown
            is_markdown = filepath.lower().endswith('.md')
            
            logger.info(f"Successfully extracted {len(raw_text)} characters from text file")
            
            return ExtractionPayload(
                raw_text=raw_text.strip(),
                meta={
                    'encoding': encoding,
                    'format': 'markdown' if is_markdown else 'text',
                    'confidence': result.get('confidence', 0.0)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to extract text content from {filepath}: {e}")
            raise ValueError(f"Text extraction failed: {str(e)}")
    
    def extract_markdown(self, filepath: str) -> str:
        """Extract Markdown content from text file.
        
        Args:
            filepath: Path to the text file
            
        Returns:
            Markdown string representation of the document
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            logger.info(f"Extracting Markdown content from {filepath}")
            
            # Use the same extraction logic, but return raw text as markdown
            payload = self.extract(filepath)
            
            return payload.raw_text
            
        except Exception as e:
            logger.error(f"Failed to extract Markdown content from {filepath}: {e}")
            raise ValueError(f"Markdown extraction failed: {str(e)}")
"""DOCX document extractor."""

import os
import docx2txt
from sentra_core.logging import get_logger
from sentra_rag_worker.services.extraction.pandoc_utils import convert_with_pandoc_to_markdown
from .base import DocumentExtractorBase, ExtractionPayload

logger = get_logger(__name__)


class DocxExtractor(DocumentExtractorBase):
    """Extract text from DOCX documents."""
    
    def extract(self, filepath: str) -> ExtractionPayload:
        """Extract content from DOCX file.
        
        Args:
            filepath: Path to the DOCX file
            
        Returns:
            ExtractionPayload with extracted text and metadata
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            logger.info(f"Extracting DOCX content from {filepath}")
            
            # Extract text using docx2txt
            raw_text = docx2txt.process(filepath)
            
            if not raw_text:
                raw_text = ""
            
            logger.info(f"Successfully extracted {len(raw_text)} characters from DOCX")
            
            return ExtractionPayload(
                raw_text=raw_text.strip(),
                meta={
                    'extractor': 'docx2txt',
                    'format': 'docx'
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to extract DOCX content from {filepath}: {e}")
            raise ValueError(f"DOCX extraction failed: {str(e)}")
    
    def extract_markdown(self, filepath: str) -> str:
        """Extract Markdown content from DOCX file using Pandoc."""
        logger.info(f"Extracting Markdown from DOCX via Pandoc: {filepath}")
        return convert_with_pandoc_to_markdown(filepath, input_format="docx")

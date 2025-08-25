
"""
Backward compatibility adapter for DocumentExtractor.

This module provides compatibility with the existing DocumentExtractor interface
while internally using the new extraction strategy pattern.
"""

from sentra_core.domain.entities.document_entity import DocumentFileType
from sentra_core.logging import get_logger
from sentra_rag_worker.services.extraction import get_extractor
from sentra_rag_worker.services.sanitizer import cast_to_markdown
import os

logger = get_logger(__name__)


class DocumentExtractor:
    """Extract clean text content from various document formats.
    
    DEPRECATED: This class is maintained for backward compatibility.
    New code should use the extraction package directly.
    """

    def extract_content(self, filepath: str, filetype: DocumentFileType) -> str:
        """Extract text content from a document file.
        
        Args:
            filepath: Path to the document file
            filetype: Document file type
            
        Returns:
            Extracted text content (plain text, not markdown)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If extraction fails
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        logger.warning("DocumentExtractor is deprecated. Use extraction package directly.")
        
        try:
            # Use new extraction strategy
            extractor = get_extractor(filetype)
            payload = extractor.extract(filepath)
            
            # For backward compatibility, return raw text without markdown casting
            return payload.raw_text
            
        except Exception as e:
            logger.error(f"Failed to extract content from {filepath}: {e}")
            raise ValueError(f"Content extraction failed: {str(e)}")

    # Keep all the old private methods to avoid breaking any direct usage
    def _extract_text_file(self, filepath: str) -> str:
        from .extraction.text_extractor import TextExtractor
        extractor = TextExtractor()
        return extractor.extract(filepath).raw_text

    def _extract_pdf(self, filepath: str) -> str:
        from .extraction.pdf_extractor import PdfExtractor
        extractor = PdfExtractor()
        return extractor.extract(filepath).raw_text

    def _extract_docx(self, filepath: str) -> str:
        from .extraction.docx_extractor import DocxExtractor
        extractor = DocxExtractor()
        return extractor.extract(filepath).raw_text

    def _extract_html(self, filepath: str) -> str:
        from .extraction.html_extractor import HtmlExtractor
        extractor = HtmlExtractor()
        return extractor.extract(filepath).raw_text

    def _extract_eml(self, filepath: str) -> str:
        from .extraction.email_extractor import EmlExtractor
        extractor = EmlExtractor()
        return extractor.extract(filepath).raw_text

    def _extract_msg(self, filepath: str) -> str:
        from .extraction.email_extractor import MsgExtractor
        extractor = MsgExtractor()
        return extractor.extract(filepath).raw_text

    def _extract_epub(self, filepath: str) -> str:
        from .extraction.epub_extractor import EpubExtractor
        extractor = EpubExtractor()
        return extractor.extract(filepath).raw_text

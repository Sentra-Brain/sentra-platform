"""Factory for creating document extractors based on file type."""

from sentra_core.domain.entities.document_entity import DocumentFileType
from .base import DocumentExtractorBase
from .pdf_extractor import PdfExtractor
from .docx_extractor import DocxExtractor
from .html_extractor import HtmlExtractor
from .text_extractor import TextExtractor
from .email_extractor import EmlExtractor, MsgExtractor
from .epub_extractor import EpubExtractor


def get_extractor(filetype: DocumentFileType) -> DocumentExtractorBase:
    """Get the appropriate extractor for a document file type.
    
    Args:
        filetype: The document file type
        
    Returns:
        Document extractor instance
        
    Raises:
        ValueError: If file type is not supported
    """
    extractors = {
        DocumentFileType.PDF: PdfExtractor,
        DocumentFileType.DOCX: DocxExtractor,
        DocumentFileType.HTML: HtmlExtractor,
        DocumentFileType.TXT: TextExtractor,
        DocumentFileType.MD: TextExtractor,
        DocumentFileType.EML: EmlExtractor,
        DocumentFileType.MSG: MsgExtractor,
        DocumentFileType.EPUB: EpubExtractor,
    }
    
    extractor_class = extractors.get(filetype)
    if not extractor_class:
        raise ValueError(f"Unsupported file type: {filetype}")
    
    return extractor_class()
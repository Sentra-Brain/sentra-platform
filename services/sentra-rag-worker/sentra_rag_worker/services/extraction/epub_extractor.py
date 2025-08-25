"""EPUB document extractor."""

import os
from ebooklib import epub
from bs4 import BeautifulSoup
from sentra_core.logging import get_logger
from sentra_rag_worker.services.extraction.pandoc_utils import convert_with_pandoc_to_markdown
from .base import DocumentExtractorBase, ExtractionPayload

logger = get_logger(__name__)


class EpubExtractor(DocumentExtractorBase):
    """Extract text from EPUB documents."""
    
    def extract(self, filepath: str) -> ExtractionPayload:
        """Extract content from EPUB file.
        
        Args:
            filepath: Path to the EPUB file
            
        Returns:
            ExtractionPayload with extracted text and metadata
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            logger.info(f"Extracting EPUB content from {filepath}")
            
            # Read EPUB book
            book = epub.read_epub(filepath)
            
            # Extract text from all HTML items
            text_parts = []
            chapter_count = 0
            
            for item in book.get_items():
                if item.get_type() == epub.EpubHtml:
                    chapter_count += 1
                    content = item.get_content()
                    
                    # Parse HTML content
                    soup = BeautifulSoup(content, 'lxml')
                    
                    # Remove script and style elements
                    for tag in soup(['script', 'style']):
                        tag.decompose()
                    
                    # Extract text
                    chapter_text = soup.get_text(separator='\n', strip=True)
                    if chapter_text:
                        text_parts.append(chapter_text)
            
            # Join all chapters
            raw_text = "\n\n".join(text_parts)
            
            # Extract metadata
            metadata = {
                'title': book.get_metadata('DC', 'title'),
                'creator': book.get_metadata('DC', 'creator'),
                'subject': book.get_metadata('DC', 'subject'),
                'description': book.get_metadata('DC', 'description'),
                'publisher': book.get_metadata('DC', 'publisher'),
                'date': book.get_metadata('DC', 'date'),
                'language': book.get_metadata('DC', 'language'),
                'rights': book.get_metadata('DC', 'rights')
            }
            
            # Extract first non-empty value for each metadata field
            clean_metadata = {}
            for key, values in metadata.items():
                if values:
                    clean_metadata[key] = values[0][0] if isinstance(values[0], tuple) else str(values[0])
            
            logger.info(f"Successfully extracted {len(raw_text)} characters from EPUB with {chapter_count} chapters")
            
            return ExtractionPayload(
                raw_text=raw_text.strip(),
                meta={
                    **clean_metadata,
                    'format': 'epub',
                    'chapter_count': chapter_count
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to extract EPUB content from {filepath}: {e}")
            raise ValueError(f"EPUB extraction failed: {str(e)}")
    
    def extract_markdown(self, filepath: str) -> str:
        """Extract Markdown content from EPUB file using Pandoc."""
        logger.info(f"Extracting Markdown from EPUB via Pandoc: {filepath}")
        return convert_with_pandoc_to_markdown(filepath, input_format="epub")

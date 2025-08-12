"""HTML document extractor."""

import os
from bs4 import BeautifulSoup
from sentra_core.core.logging import get_logger
from sentra_rag_worker.services.extraction.pandoc_utils import convert_with_pandoc_to_markdown
from .base import DocumentExtractorBase, ExtractionPayload

logger = get_logger(__name__)


class HtmlExtractor(DocumentExtractorBase):
    """Extract text from HTML documents."""
    
    def extract(self, filepath: str) -> ExtractionPayload:
        """Extract content from HTML file.
        
        Args:
            filepath: Path to the HTML file
            
        Returns:
            ExtractionPayload with extracted text and HTML blocks
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            logger.info(f"Extracting HTML content from {filepath}")
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'lxml')
            
            # Remove script and style elements
            for tag in soup(['script', 'style']):
                tag.decompose()
            
            # Extract title if available
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else None
            
            # Extract main content blocks
            html_blocks = []
            for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'article', 'section']):
                block_text = tag.get_text(separator=' ', strip=True)
                if block_text:
                    html_blocks.append(block_text)
            
            # Get full text content
            raw_text = soup.get_text(separator='\n', strip=True)
            
            logger.info(f"Successfully extracted {len(raw_text)} characters from HTML with {len(html_blocks)} blocks")
            
            return ExtractionPayload(
                raw_text=raw_text,
                html_blocks=html_blocks,
                meta={
                    'title': title,
                    'format': 'html',
                    'blocks_count': len(html_blocks)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to extract HTML content from {filepath}: {e}")
            raise ValueError(f"HTML extraction failed: {str(e)}")
        
    def extract_markdown(self, filepath: str) -> str:
        """Extract Markdown content from HTML file using Pandoc."""
        logger.info(f"Extracting Markdown from HTML via Pandoc: {filepath}")
        return convert_with_pandoc_to_markdown(filepath, input_format="html")
        
"""Tests for document extraction strategy pattern."""

import os
import tempfile
import pytest
from pathlib import Path
from sentra.domain.entities.document_entity import DocumentFileType
from sentra_rag_worker.services.extraction import get_extractor, ExtractionPayload
from sentra_rag_worker.services.extraction.pdf_extractor import PdfExtractor
from sentra_rag_worker.services.extraction.text_extractor import TextExtractor
from sentra_rag_worker.services.extraction.html_extractor import HtmlExtractor


def test_get_extractor_factory():
    """Test that factory returns correct extractors."""
    pdf_extractor = get_extractor(DocumentFileType.PDF)
    assert isinstance(pdf_extractor, PdfExtractor)
    
    text_extractor = get_extractor(DocumentFileType.TXT)
    assert isinstance(text_extractor, TextExtractor)
    
    html_extractor = get_extractor(DocumentFileType.HTML)
    assert isinstance(html_extractor, HtmlExtractor)
    
    # Test unsupported type
    with pytest.raises(ValueError):
        get_extractor("unsupported")


def test_text_extractor():
    """Test text file extraction."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        test_content = "This is a test document.\nIt has multiple lines.\n\nAnd paragraphs."
        f.write(test_content)
        f.flush()
        
        try:
            extractor = TextExtractor()
            payload = extractor.extract(f.name)
            
            assert isinstance(payload, ExtractionPayload)
            assert payload.raw_text.strip() == test_content.strip()
            assert payload.word_count > 0
            assert payload.meta['format'] == 'text'
            assert payload.pages is None
            
        finally:
            os.unlink(f.name)


def test_html_extractor():
    """Test HTML file extraction."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        html_content = """
        <html>
        <head><title>Test Document</title></head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a paragraph.</p>
            <script>console.log('script');</script>
            <style>body { color: red; }</style>
        </body>
        </html>
        """
        f.write(html_content)
        f.flush()
        
        try:
            extractor = HtmlExtractor()
            payload = extractor.extract(f.name)
            
            assert isinstance(payload, ExtractionPayload)
            assert "Main Heading" in payload.raw_text
            assert "This is a paragraph" in payload.raw_text
            assert "console.log" not in payload.raw_text  # Script removed
            assert "color: red" not in payload.raw_text  # Style removed
            assert payload.meta['title'] == 'Test Document'
            assert payload.html_blocks is not None
            assert len(payload.html_blocks) > 0
            
        finally:
            os.unlink(f.name)


def test_extraction_payload():
    """Test ExtractionPayload dataclass."""
    payload = ExtractionPayload(
        raw_text="This is a test with five words",
        pages=2,
        meta={'title': 'Test'}
    )
    
    assert payload.word_count == 7  # "This is a test with five words"
    assert payload.pages == 2
    assert payload.meta['title'] == 'Test'
    
    # Test empty text
    empty_payload = ExtractionPayload(raw_text="")
    assert empty_payload.word_count == 0


def test_file_not_found():
    """Test that extractors handle missing files properly."""
    extractor = TextExtractor()
    
    with pytest.raises(FileNotFoundError):
        extractor.extract("/nonexistent/file.txt")


if __name__ == "__main__":
    pytest.main([__file__])
"""Tests for metadata detection functionality."""

import tempfile
import pytest
from sentra_core.domain.entities.document_entity import DocumentFileType
from sentra_rag_worker.services.extraction.base import ExtractionPayload
from sentra_rag_worker.services.metadata.detectors import (
    detect_title,
    detect_language,
    extract_headings,
    extract_links,
    extract_metadata
)


def test_detect_title_from_metadata():
    """Test title detection from document metadata."""
    payload = ExtractionPayload(
        raw_text="Some content",
        meta={'title': 'Document Title from Metadata'}
    )
    
    title = detect_title(payload, DocumentFileType.PDF, "/path/file.pdf", "file.pdf")
    assert title == "Document Title from Metadata"


def test_detect_title_from_email_subject():
    """Test title detection from email subject."""
    payload = ExtractionPayload(
        raw_text="Email body content",
        email_headers={'subject': 'Important Email Subject'}
    )
    
    title = detect_title(payload, DocumentFileType.EML, "/path/email.eml", "email.eml")
    assert title == "Important Email Subject"


def test_detect_title_from_heading():
    """Test title detection from first heading in text."""
    payload = ExtractionPayload(
        raw_text="# Main Document Title\n\nThis is the content of the document."
    )
    
    title = detect_title(payload, DocumentFileType.MD, "/path/doc.md", "doc.md")
    assert title == "Main Document Title"


def test_detect_title_from_filename():
    """Test title detection from filename as fallback."""
    payload = ExtractionPayload(raw_text="")  # Empty text so filename is used
    
    title = detect_title(payload, DocumentFileType.TXT, "/path/my_document_2024.txt", "my_document_2024.txt")
    assert title == "My Document"  # Should clean up filename


def test_detect_language_english():
    """Test English language detection."""
    english_text = "The quick brown fox jumps over the lazy dog. This is a test of the English language detection system."
    
    language = detect_language(english_text)
    assert language == "en"


def test_detect_language_spanish():
    """Test Spanish language detection."""
    spanish_text = "El perro come la comida. La casa es muy grande y tiene un jardín hermoso en el frente."
    
    language = detect_language(spanish_text)
    assert language == "es"


def test_detect_language_uncertain():
    """Test language detection with uncertain text."""
    short_text = "ABC 123"
    unclear_text = "xyzabc defghi jklmno"
    
    assert detect_language(short_text) is None
    assert detect_language(unclear_text) is None


def test_extract_headings():
    """Test heading extraction from markdown text."""
    markdown_text = """# Main Title

## Section One

Some content here.

### Subsection

More content.

## Section Two

Final content."""
    
    headings = extract_headings(markdown_text)
    
    assert "Main Title" in headings
    assert "Section One" in headings
    assert "Subsection" in headings
    assert "Section Two" in headings
    assert len(headings) == 4


def test_extract_links():
    """Test link extraction from text."""
    text_with_links = """
    Check out https://example.com for more info.
    Also see [this link](https://test.com) for details.
    And visit http://another-site.org/path?param=value.
    """
    
    links = extract_links(text_with_links)
    
    assert "https://example.com" in links
    assert "https://test.com" in links  
    assert "http://another-site.org/path?param=value" in links
    assert len(links) == 3


def test_extract_metadata_comprehensive():
    """Test comprehensive metadata extraction."""
    payload = ExtractionPayload(
        raw_text="This is a test document with multiple words for testing.",
        pages=3,
        meta={'title': 'Test Document', 'author': 'Test Author'},
        email_headers=None
    )
    
    markdown_text = "# Test Document\n\nContent with [link](https://example.com)."
    
    with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
        metadata = extract_metadata(
            payload, 
            markdown_text, 
            DocumentFileType.PDF, 
            tmp.name, 
            "test_document.pdf"
        )
    
    assert metadata['internal_title'] == "test_document.pdf"
    assert metadata['extracted_title'] == "Test Document"
    assert metadata['file_type'] == "pdf"
    assert metadata['word_count'] == 10  # Count words in raw_text
    assert metadata['page_count'] == 3
    assert metadata['headings'] == ["Test Document"]
    assert metadata['links'] == ["https://example.com"]
    assert metadata['mime'] == "application/pdf"


def test_extract_metadata_email():
    """Test metadata extraction for email documents."""
    payload = ExtractionPayload(
        raw_text="Email body content here.",
        email_headers={
            'subject': 'Test Email',
            'from': 'sender@example.com',
            'date': '2024-01-01'
        }
    )
    
    markdown_text = "# Test Email\n\nEmail body content here."
    
    metadata = extract_metadata(
        payload,
        markdown_text,
        DocumentFileType.EML,
        "/path/email.eml",
        "email.eml"
    )
    
    assert metadata['extracted_title'] == "Test Email"
    assert metadata['email_from'] == "sender@example.com"
    assert metadata['email_date'] == "2024-01-01"
    assert metadata['mime'] == "message/rfc822"


def test_extract_metadata_html():
    """Test metadata extraction for HTML documents."""
    payload = ExtractionPayload(
        raw_text="HTML content here",
        html_blocks=["Block 1", "Block 2"],
        meta={'blocks_count': 2}
    )
    
    markdown_text = "HTML content here"
    
    metadata = extract_metadata(
        payload,
        markdown_text,
        DocumentFileType.HTML,
        "/path/page.html",
        "page.html"
    )
    
    assert metadata['html_blocks_count'] == 2
    assert metadata['mime'] == "text/html"


def test_empty_metadata():
    """Test metadata extraction with minimal data."""
    payload = ExtractionPayload(raw_text="")
    
    metadata = extract_metadata(
        payload,
        "",
        DocumentFileType.TXT,
        "/path/empty.txt",
        "empty.txt"
    )
    
    assert metadata['internal_title'] == "empty.txt"
    assert metadata['file_type'] == "txt"
    assert metadata['word_count'] == 0
    # Should not include None values
    assert 'extracted_title' not in metadata or metadata['extracted_title'] is not None


if __name__ == "__main__":
    pytest.main([__file__])
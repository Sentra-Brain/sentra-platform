"""Tests for markdown casting functionality."""

import pytest
from sentra_core.domain.entities.document_entity import DocumentFileType
from sentra_rag_worker.services.sanitizer import (
    html_to_md, 
    pdf_to_md, 
    docx_to_md, 
    email_to_md, 
    plain_to_md,
    cast_to_markdown
)
from sentra_rag_worker.services.sanitizer.common import (
    normalize_whitespace,
    convert_pagebreaks,
    normalize_unicode
)


def test_html_to_md():
    """Test HTML to Markdown conversion."""
    html = """
    <h1>Main Title</h1>
    <p>This is a paragraph with <strong>bold</strong> text.</p>
    <ul>
        <li>First item</li>
        <li>Second item</li>
    </ul>
    <a href="https://example.com">Link text</a>
    <script>alert('remove me');</script>
    """
    
    result = html_to_md(html)
    
    assert "# Main Title" in result
    assert "This is a paragraph" in result
    assert "- First item" in result
    assert "- Second item" in result
    assert "[Link text](https://example.com)" in result
    assert "alert('remove me')" not in result


def test_pdf_to_md():
    """Test PDF text to Markdown conversion."""
    pdf_text = "Page 1 content\f\nPage 2 content\fPage 3 content"
    
    result = pdf_to_md(pdf_text, pages=3)
    
    assert "Page 1 content" in result
    assert "Page 2 content" in result 
    assert "Page 3 content" in result
    assert "---" in result  # Page separators


def test_docx_to_md():
    """Test DOCX text to Markdown conversion."""
    docx_text = """Title Document
    
    • First bullet point
    • Second bullet point
    
    1. Numbered item one
    2. Numbered item two
    
    Regular paragraph text."""
    
    result = docx_to_md(docx_text)
    
    assert "## Title Document" in result
    assert "- First bullet point" in result
    assert "- Second bullet point" in result
    assert "1. Numbered item one" in result
    assert "Regular paragraph text" in result


def test_email_to_md():
    """Test email to Markdown conversion."""
    email_body = "Hello,\n\nThis is the email body.\n\nBest regards,\nSender"
    headers = {
        'subject': 'Test Email Subject',
        'from': 'sender@example.com',
        'date': '2024-01-01T12:00:00Z'
    }
    
    result = email_to_md(email_body, headers)
    
    assert "# Test Email Subject" in result
    assert "**From:** sender@example.com" in result
    assert "**Date:** 2024-01-01T12:00:00Z" in result
    assert "This is the email body" in result


def test_plain_to_md():
    """Test plain text to Markdown conversion."""
    text = "This is plain text.\n\n  With   extra    spaces   \n\nAnd multiple lines."
    
    result = plain_to_md(text)
    
    assert "This is plain text" in result
    assert "With extra spaces" in result  # Normalized whitespace
    assert "And multiple lines" in result


def test_cast_to_markdown():
    """Test the main casting function with different file types."""
    # Test HTML
    html_result = cast_to_markdown(
        "<h1>Title</h1><p>Content</p>", 
        DocumentFileType.HTML
    )
    assert "# Title" in html_result
    
    # Test PDF  
    pdf_result = cast_to_markdown(
        "Page 1\fPage 2", 
        DocumentFileType.PDF,
        pages=2
    )
    assert "---" in pdf_result
    
    # Test email
    email_result = cast_to_markdown(
        "Email body", 
        DocumentFileType.EML,
        email_headers={'subject': 'Test'}
    )
    assert "# Test" in email_result


def test_normalize_whitespace():
    """Test whitespace normalization."""
    text = "Text   with    multiple   spaces\n\n\n\nAnd   blank  lines"
    result = normalize_whitespace(text)
    
    assert "Text with multiple spaces" in result
    assert "And blank lines" in result
    # Should remove excessive blank lines


def test_convert_pagebreaks():
    """Test page break conversion."""
    text = "Page 1\fPage 2\f\fPage 3"
    result = convert_pagebreaks(text)
    
    assert "Page 1\n\n---\n\nPage 2" in result
    assert "Page 3" in result
    # Should not have consecutive separators


def test_normalize_unicode():
    """Test unicode normalization."""
    text = 'Text with "smart quotes" and – dashes'
    result = normalize_unicode(text)
    
    assert '"smart quotes"' in result
    assert '- dashes' in result


def test_empty_inputs():
    """Test that functions handle empty inputs gracefully."""
    assert html_to_md("") == ""
    assert pdf_to_md("") == ""
    assert docx_to_md("") == ""
    assert email_to_md("", {}) == ""
    assert plain_to_md("") == ""
    
    assert cast_to_markdown("", DocumentFileType.TXT) == ""


if __name__ == "__main__":
    pytest.main([__file__])
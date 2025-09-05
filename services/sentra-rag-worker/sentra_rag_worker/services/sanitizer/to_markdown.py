"""Markdown casting functions for different document types."""

import re
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from sentra.domain.entities.document_entity import DocumentFileType
from .common import clean_text, convert_pagebreaks, normalize_unicode


def html_to_md(html_text: str, html_blocks: Optional[List[str]] = None) -> str:
    """Convert HTML text to Markdown.
    
    Args:
        html_text: Raw HTML text
        html_blocks: Optional list of HTML blocks for structure
        
    Returns:
        Markdown formatted text
    """
    if not html_text:
        return ""
    
    try:
        soup = BeautifulSoup(html_text, 'lxml')
        
        # Remove script and style elements
        for tag in soup(['script', 'style', 'meta', 'link']):
            tag.decompose()
        
        markdown_lines = []
        
        # Process elements in order
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'a', 'img']):
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.name[1])
                text = element.get_text().strip()
                if text:
                    markdown_lines.append(f"{'#' * level} {text}")
                    
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    markdown_lines.append(text)
                    
            elif element.name == 'ul':
                for li in element.find_all('li', recursive=False):
                    text = li.get_text().strip()
                    if text:
                        markdown_lines.append(f"- {text}")
                        
            elif element.name == 'ol':
                for i, li in enumerate(element.find_all('li', recursive=False), 1):
                    text = li.get_text().strip()
                    if text:
                        markdown_lines.append(f"{i}. {text}")
                        
            elif element.name == 'blockquote':
                text = element.get_text().strip()
                if text:
                    quoted = '\n'.join(f"> {line}" for line in text.split('\n'))
                    markdown_lines.append(quoted)
                    
            elif element.name == 'pre':
                text = element.get_text()
                if text:
                    markdown_lines.append(f"```\n{text}\n```")
                    
            elif element.name == 'code' and element.parent.name != 'pre':
                text = element.get_text().strip()
                if text:
                    markdown_lines.append(f"`{text}`")
                    
            elif element.name == 'a':
                text = element.get_text().strip()
                href = element.get('href', '')
                if text and href:
                    markdown_lines.append(f"[{text}]({href})")
                    
            elif element.name == 'img':
                alt = element.get('alt', '')
                src = element.get('src', '')
                if src:
                    markdown_lines.append(f"![{alt}]({src})")
        
        # If no structured content found, fall back to plain text
        if not markdown_lines:
            return clean_text(soup.get_text())
        
        result = '\n\n'.join(markdown_lines)
        return clean_text(result)
        
    except Exception:
        # Fall back to plain text if parsing fails
        return clean_text(html_text)


def pdf_to_md(raw_text: str, pages: Optional[int] = None) -> str:
    """Convert PDF text to Markdown.
    
    Args:
        raw_text: Raw text from PDF
        pages: Number of pages
        
    Returns:
        Markdown formatted text
    """
    if not raw_text:
        return ""
    
    # Convert page breaks to markdown separators
    text = convert_pagebreaks(raw_text)
    
    # Try to detect headings by looking for lines that are all caps or have specific patterns
    lines = text.split('\n')
    markdown_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            markdown_lines.append('')
            continue
            
        # Simple heuristic for headings - all caps lines that are short
        if (line.isupper() and len(line) < 100 and 
            not line.startswith('-') and
            not re.match(r'^\d+\.', line)):
            markdown_lines.append(f"## {line.title()}")
        else:
            markdown_lines.append(line)
    
    result = '\n'.join(markdown_lines)
    return clean_text(result)


def docx_to_md(raw_text: str) -> str:
    """Convert DOCX text to Markdown.
    
    Args:
        raw_text: Raw text from DOCX
        
    Returns:
        Markdown formatted text
    """
    if not raw_text:
        return ""
    
    lines = raw_text.split('\n')
    markdown_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            markdown_lines.append('')
            continue
        
        # Detect bullet points
        if line.startswith('• ') or line.startswith('- '):
            markdown_lines.append(f"- {line[2:]}")
        # Detect numbered lists
        elif re.match(r'^\d+\.\s', line):
            markdown_lines.append(line)
        # Try to detect headings (lines that are short and don't end with punctuation)
        elif (len(line) < 100 and 
              not line.endswith('.') and 
              not line.endswith(',') and
              not line.endswith(':') and
              len(line.split()) < 10):
            markdown_lines.append(f"## {line}")
        else:
            markdown_lines.append(line)
    
    result = '\n'.join(markdown_lines)
    return clean_text(result)


def email_to_md(text: str, headers: Optional[Dict[str, str]] = None) -> str:
    """Convert email text to Markdown.
    
    Args:
        text: Email body text
        headers: Email headers
        
    Returns:
        Markdown formatted text
    """
    if not text and not headers:
        return ""
    
    markdown_parts = []
    
    # Add subject as title if available
    if headers and headers.get('subject'):
        markdown_parts.append(f"# {headers['subject']}")
        markdown_parts.append("")
    
    # Add metadata block
    if headers:
        metadata_lines = []
        for key, value in headers.items():
            if value and key != 'subject':
                markdown_parts.append(f"**{key.title()}:** {value}")
        
        if metadata_lines:
            markdown_parts.extend(metadata_lines)
            markdown_parts.append("")
    
    # Add body content
    if text:
        # Clean and format the body
        body = clean_text(text)
        markdown_parts.append(body)
    
    return '\n'.join(markdown_parts)


def plain_to_md(text: str) -> str:
    """Convert plain text to Markdown.
    
    Args:
        text: Plain text
        
    Returns:
        Markdown formatted text (minimal changes)
    """
    if not text:
        return ""
    
    # For plain text and markdown, just clean it up
    return clean_text(text)


def cast_to_markdown(raw_text: str, filetype: DocumentFileType, **kwargs) -> str:
    """Cast text to markdown based on document type.
    
    Args:
        raw_text: Raw extracted text
        filetype: Document file type
        **kwargs: Additional arguments specific to each type
        
    Returns:
        Markdown formatted text
    """
    if not raw_text:
        return ""
    
    if filetype == DocumentFileType.HTML:
        return html_to_md(raw_text, kwargs.get('html_blocks'))
    elif filetype == DocumentFileType.PDF:
        return pdf_to_md(raw_text, kwargs.get('pages'))
    elif filetype == DocumentFileType.DOCX:
        return docx_to_md(raw_text)
    elif filetype in [DocumentFileType.EML, DocumentFileType.MSG]:
        return email_to_md(raw_text, kwargs.get('email_headers'))
    elif filetype in [DocumentFileType.TXT, DocumentFileType.MD, DocumentFileType.EPUB]:
        return plain_to_md(raw_text)
    else:
        # Fallback to plain text cleaning
        return clean_text(raw_text)
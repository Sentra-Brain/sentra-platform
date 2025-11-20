"""Metadata detection and enrichment functions."""

import re
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from sentra.domain.entities.document_entity import DocumentFileType
from sentra_rag_worker.services.extraction.base import ExtractionPayload


def detect_title(
    payload: ExtractionPayload, 
    filetype: DocumentFileType, 
    filepath: str,
    filename: str
) -> Optional[str]:
    """Detect the best title for a document.
    
    Priority order:
    1. Document metadata title (PDF, EPUB, etc.)
    2. Email subject (EML/MSG)
    3. First heading in markdown text
    4. HTML title tag
    5. Filename without extension
    
    Args:
        payload: Extraction result
        filetype: Document file type
        filepath: Full file path
        filename: Just the filename
        
    Returns:
        Detected title or None
    """
    # 1. Check document metadata
    if payload.meta and payload.meta.get('title'):
        title = payload.meta['title']
        if isinstance(title, list) and title:
            title = title[0]
        if title and isinstance(title, str) and title.strip():
            return title.strip()
    
    # 2. Check email subject
    if payload.email_headers and payload.email_headers.get('subject'):
        subject = payload.email_headers['subject']
        if subject and subject.strip():
            return subject.strip()
    
    # 3. Check for first heading in text
    if payload.raw_text:
        lines = payload.raw_text.split('\n')[:20]  # Check first 20 lines
        for line in lines:
            line = line.strip()
            # Markdown heading
            if line.startswith('#'):
                heading = line.lstrip('#').strip()
                if heading:
                    return heading
            # Potential title (short line at start of document)
            elif (len(line) < 200 and len(line) > 5 and 
                  not line.endswith('.') and
                  not line.startswith('http')):
                return line
    
    # 4. Extract from filename
    if filename:
        # Remove extension and clean up
        name = Path(filename).stem
        # Replace underscores and hyphens with spaces
        name = re.sub(r'[_-]', ' ', name)
        # Remove common patterns
        name = re.sub(r'\d{4}(-\d{2})?(-\d{2})?', '', name)  # Remove dates and years
        name = re.sub(r'\s+', ' ', name).strip()
        if name and len(name) > 2:
            return name.title()
    
    return None


def detect_language(text: str) -> Optional[str]:
    """Detect language of text using simple heuristics.
    
    Args:
        text: Text to analyze
        
    Returns:
        Language code or None if uncertain
    """
    if not text or len(text) < 50:
        return None
    
    # Simple heuristics for common languages
    text_lower = text.lower()
    
    # English indicators
    english_words = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with', 'for', 'as', 'was', 'on', 'are']
    english_score = sum(1 for word in english_words if f' {word} ' in text_lower)
    
    # Spanish indicators  
    spanish_words = ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su']
    spanish_score = sum(1 for word in spanish_words if f' {word} ' in text_lower)
    
    # French indicators
    french_words = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour', 'dans', 'ce', 'son']
    french_score = sum(1 for word in french_words if f' {word} ' in text_lower)
    
    # Simple scoring
    if english_score >= 3 and english_score >= spanish_score and english_score >= french_score:
        return 'en'
    elif spanish_score >= 3 and spanish_score > english_score and spanish_score >= french_score:
        return 'es'
    elif french_score >= 3 and french_score > english_score and french_score > spanish_score:
        return 'fr'
    
    return None


def extract_headings(text: str) -> List[str]:
    """Extract headings from markdown text.
    
    Args:
        text: Markdown text
        
    Returns:
        List of headings
    """
    if not text:
        return []
    
    headings = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        # Markdown headings
        if line.startswith('#'):
            heading = line.lstrip('#').strip()
            if heading:
                headings.append(heading)
    
    return headings


def extract_links(text: str) -> List[str]:
    """Extract links from text.
    
    Args:
        text: Text to search for links
        
    Returns:
        List of URLs found
    """
    if not text:
        return []
    
    # Find URLs (basic pattern)
    url_pattern = r'https?://[^\s\)]+' 
    urls = re.findall(url_pattern, text)
    
    # Find markdown links
    markdown_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    markdown_links = re.findall(markdown_pattern, text)
    urls.extend([link[1] for link in markdown_links])
    
    # Deduplicate and clean
    unique_urls = list(set(urls))
    return [url.rstrip('.,;:') for url in unique_urls]


def extract_metadata(
    payload: ExtractionPayload,
    text_md: str,
    filetype: DocumentFileType,
    filepath: str,
    filename: str
) -> Dict[str, Any]:
    """Extract comprehensive metadata from document.
    
    Args:
        payload: Extraction result
        text_md: Markdown-formatted text
        filetype: Document file type
        filepath: Full file path
        filename: Just the filename
        
    Returns:
        Dictionary of metadata
    """
    metadata = {
        'internal_title': filename,
        'extracted_title': detect_title(payload, filetype, filepath, filename),
        'file_type': filetype.value,
        'word_count': payload.word_count,
        'language': detect_language(payload.raw_text),
        'headings': extract_headings(text_md),
        'links': extract_links(text_md),
        'mime': _get_mime_type(filetype),
        'file_size': _get_file_size(filepath)
    }
    
    # Add type-specific metadata
    if payload.pages is not None:
        metadata['page_count'] = payload.pages
    
    if payload.email_headers:
        metadata['email_from'] = payload.email_headers.get('from')
        metadata['email_date'] = payload.email_headers.get('date')
    
    if payload.meta:
        # Add document-specific metadata
        if filetype == DocumentFileType.PDF:
            metadata['pdf_author'] = payload.meta.get('author')
            metadata['pdf_subject'] = payload.meta.get('subject')
            metadata['pdf_creator'] = payload.meta.get('creator')
        elif filetype == DocumentFileType.EPUB:
            metadata['epub_publisher'] = payload.meta.get('publisher')
            metadata['epub_description'] = payload.meta.get('description')
        elif filetype == DocumentFileType.HTML:
            metadata['html_blocks_count'] = payload.meta.get('blocks_count')
    
    # Clean up None values
    return {k: v for k, v in metadata.items() if v is not None}


def _get_mime_type(filetype: DocumentFileType) -> str:
    """Get MIME type for file type."""
    mime_types = {
        DocumentFileType.PDF: 'application/pdf',
        DocumentFileType.DOCX: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        DocumentFileType.HTML: 'text/html',
        DocumentFileType.TXT: 'text/plain',
        DocumentFileType.MD: 'text/markdown',
        DocumentFileType.EML: 'message/rfc822',
        DocumentFileType.MSG: 'application/vnd.ms-outlook',
        DocumentFileType.EPUB: 'application/epub+zip'
    }
    return mime_types.get(filetype, 'application/octet-stream')


def _get_file_size(filepath: str) -> Optional[int]:
    """Get file size in bytes."""
    try:
        return os.path.getsize(filepath)
    except (OSError, IOError):
        return None
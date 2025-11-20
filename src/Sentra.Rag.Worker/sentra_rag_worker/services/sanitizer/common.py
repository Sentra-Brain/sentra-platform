"""Common text sanitization utilities."""

import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.
    
    Args:
        text: Input text
        
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    
    # Remove empty lines and rejoin
    lines = [line for line in lines if line]
    
    return '\n'.join(lines)


def normalize_unicode(text: str) -> str:
    """Normalize unicode characters.
    
    Args:
        text: Input text
        
    Returns:
        Text with normalized unicode
    """
    if not text:
        return ""
    
    # Normalize unicode characters to NFC form
    text = unicodedata.normalize('NFC', text)
    
    # Replace common problematic characters
    replacements = {
        '"': '"',  # Left double quotation mark
        '"': '"',  # Right double quotation mark
        ''': "'",  # Left single quotation mark  
        ''': "'",  # Right single quotation mark
        '–': '-',  # En dash
        '—': '--', # Em dash
        '…': '...', # Horizontal ellipsis
        '\xa0': ' ', # Non-breaking space
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def convert_pagebreaks(text: str) -> str:
    """Convert page break characters to markdown separators.
    
    Args:
        text: Input text with page breaks (form feed characters)
        
    Returns:
        Text with page breaks converted to markdown separators
    """
    if not text:
        return ""
    
    # Replace form feed characters with markdown horizontal rules
    text = text.replace('\f', '\n\n---\n\n')
    
    # Clean up multiple consecutive separators
    text = re.sub(r'\n\n---\n\n(\n\n---\n\n)+', '\n\n---\n\n', text)
    
    return text


def clean_text(text: str) -> str:
    """Apply all common text cleaning operations.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    text = normalize_unicode(text)
    text = convert_pagebreaks(text)
    text = normalize_whitespace(text)
    
    return text.strip()
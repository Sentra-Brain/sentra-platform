"""Metadata detection and enrichment utilities."""

from .detectors import (
    detect_title,
    detect_language, 
    extract_headings,
    extract_links,
    extract_metadata
)

__all__ = [
    "detect_title",
    "detect_language", 
    "extract_headings",
    "extract_links", 
    "extract_metadata"
]
"""Document extraction package with strategy pattern for different file types."""

from .base import DocumentExtractorBase, ExtractionPayload
from .factory import get_extractor

__all__ = ["DocumentExtractorBase", "ExtractionPayload", "get_extractor"]
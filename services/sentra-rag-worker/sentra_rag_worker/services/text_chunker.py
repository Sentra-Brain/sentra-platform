from typing import List
import re
from sentra_rag_worker.core.config import settings
from sentra_shared.core.logging import get_logger

logger = get_logger(__name__)


class TextChunker:
    """Split text into overlapping chunks for embedding."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("Chunk overlap must be less than chunk size")

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text: The text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []

        # Clean the text
        text = self._clean_text(text)
        
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If we're not at the end, try to break at a sentence or word boundary
            if end < len(text):
                chunk = text[start:end]
                
                # Try to break at sentence boundary first
                sentence_break = self._find_sentence_break(chunk)
                if sentence_break > len(chunk) * 0.7:  # Only if we find a good sentence break
                    chunk = text[start:start + sentence_break]
                else:
                    # Fall back to word boundary
                    word_break = self._find_word_break(chunk)
                    if word_break > len(chunk) * 0.7:  # Only if we find a good word break
                        chunk = text[start:start + word_break]
                    # Otherwise, use the full chunk
            else:
                chunk = text[start:]
            
            chunks.append(chunk.strip())
            
            # Move start position with overlap
            if end >= len(text):
                break
                
            start = max(start + len(chunk) - self.chunk_overlap, start + 1)

        logger.info(f"Split text into {len(chunks)} chunks")
        return [chunk for chunk in chunks if chunk.strip()]

    def _clean_text(self, text: str) -> str:
        """Clean text by normalizing whitespace."""
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    def _find_sentence_break(self, text: str) -> int:
        """Find the last sentence boundary in the text."""
        # Look for sentence endings (., !, ?) followed by space or end
        sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        
        last_break = -1
        for ending in sentence_endings:
            pos = text.rfind(ending)
            if pos > last_break:
                last_break = pos + len(ending) - 1  # Include the punctuation but not the space
        
        return last_break if last_break > 0 else len(text)

    def _find_word_break(self, text: str) -> int:
        """Find the last word boundary in the text."""
        # Find the last space
        last_space = text.rfind(' ')
        return last_space if last_space > 0 else len(text)
from typing import List, Dict, Optional
import re
import json
import os
from dataclasses import dataclass
from sentra_rag_worker.core.config import settings
from sentra_core.core.logging import get_logger
from sentra_core.domain.entities.document_entity import DocumentFileType

logger = get_logger(__name__)


@dataclass
class ChunkProfile:
    """Configuration for chunking strategy."""
    size: int
    overlap: int
    prefer_headers: bool = True
    prefer_paragraphs: bool = True


# Default chunk profiles by document type
DEFAULT_CHUNK_PROFILES = {
    DocumentFileType.PDF: ChunkProfile(size=1200, overlap=200, prefer_headers=True, prefer_paragraphs=True),
    DocumentFileType.HTML: ChunkProfile(size=1500, overlap=200, prefer_headers=True, prefer_paragraphs=True),
    DocumentFileType.MD: ChunkProfile(size=1600, overlap=150, prefer_headers=True, prefer_paragraphs=True),
    DocumentFileType.DOCX: ChunkProfile(size=1400, overlap=200, prefer_headers=True, prefer_paragraphs=True),
    DocumentFileType.TXT: ChunkProfile(size=1000, overlap=200, prefer_headers=False, prefer_paragraphs=True),
    DocumentFileType.EML: ChunkProfile(size=1200, overlap=150, prefer_headers=False, prefer_paragraphs=True),
    DocumentFileType.MSG: ChunkProfile(size=1200, overlap=150, prefer_headers=False, prefer_paragraphs=True),
    DocumentFileType.EPUB: ChunkProfile(size=1600, overlap=200, prefer_headers=True, prefer_paragraphs=True),
}


def load_chunk_profiles() -> Dict[DocumentFileType, ChunkProfile]:
    """Load chunk profiles from environment or use defaults."""
    profiles = DEFAULT_CHUNK_PROFILES.copy()
    
    # Try to load custom profiles from environment
    profiles_json = os.environ.get('CHUNK_PROFILES_JSON')
    if profiles_json:
        try:
            custom_profiles = json.loads(profiles_json)
            for filetype_str, profile_dict in custom_profiles.items():
                try:
                    filetype = DocumentFileType(filetype_str)
                    profile = ChunkProfile(
                        size=profile_dict.get('size', profiles[filetype].size),
                        overlap=profile_dict.get('overlap', profiles[filetype].overlap),
                        prefer_headers=profile_dict.get('prefer_headers', profiles[filetype].prefer_headers),
                        prefer_paragraphs=profile_dict.get('prefer_paragraphs', profiles[filetype].prefer_paragraphs)
                    )
                    profiles[filetype] = profile
                    logger.info(f"Loaded custom chunk profile for {filetype.value}")
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid chunk profile for {filetype_str}: {e}")
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid CHUNK_PROFILES_JSON format: {e}")
    
    return profiles


class TextChunker:
    """Split text into overlapping chunks with adaptive strategies."""

    def __init__(
        self, 
        chunk_size: int = None, 
        chunk_overlap: int = None,
        profile: Optional[ChunkProfile] = None
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.profile = profile
        self.chunk_profiles = load_chunk_profiles()
        
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("Chunk overlap must be less than chunk size")

    def chunk_text(
        self, 
        text: str, 
        filetype: Optional[DocumentFileType] = None
    ) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text: The text to chunk
            filetype: Document file type for adaptive strategy
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []

        # Get chunking profile
        profile = self._get_chunk_profile(filetype)
        
        # Clean the text
        text = self._clean_text(text)
        
        if len(text) <= profile.size:
            return [text]

        chunks = []
        
        # Try structure-aware chunking first
        if profile.prefer_headers:
            header_chunks = self._chunk_by_headers(text, profile)
            if header_chunks:
                return header_chunks
        
        if profile.prefer_paragraphs:
            paragraph_chunks = self._chunk_by_paragraphs(text, profile)
            if paragraph_chunks:
                return paragraph_chunks
        
        # Fall back to sentence-aware chunking
        chunks = self._chunk_by_sentences(text, profile)
        
        logger.info(f"Split text into {len(chunks)} chunks using profile: size={profile.size}, overlap={profile.overlap}")
        return [chunk for chunk in chunks if chunk.strip()]

    def _get_chunk_profile(self, filetype: Optional[DocumentFileType]) -> ChunkProfile:
        """Get chunking profile for file type."""
        if self.profile:
            return self.profile
        
        if filetype and filetype in self.chunk_profiles:
            return self.chunk_profiles[filetype]
        
        # Default profile
        return ChunkProfile(size=self.chunk_size, overlap=self.chunk_overlap)

    def _chunk_by_headers(self, text: str, profile: ChunkProfile) -> List[str]:
        """Chunk text by markdown headers."""
        # Split on headers
        header_pattern = r'\n(#{1,6}\s+.+)\n'
        parts = re.split(header_pattern, text)
        
        if len(parts) <= 1:
            return []  # No headers found
        
        chunks = []
        current_chunk = ""
        
        for i in range(0, len(parts)):
            part = parts[i].strip()
            if not part:
                continue
                
            # Check if adding this part would exceed chunk size
            potential_chunk = current_chunk + "\n\n" + part if current_chunk else part
            
            if len(potential_chunk) <= profile.size:
                current_chunk = potential_chunk
            else:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Start new chunk
                if len(part) <= profile.size:
                    current_chunk = part
                else:
                    # Split large part by sentences
                    large_chunks = self._chunk_by_sentences(part, profile)
                    chunks.extend(large_chunks[:-1])  # Add all but last
                    current_chunk = large_chunks[-1] if large_chunks else ""
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def _chunk_by_paragraphs(self, text: str, profile: ChunkProfile) -> List[str]:
        """Chunk text by paragraphs."""
        paragraphs = re.split(r'\n\s*\n', text)
        
        if len(paragraphs) <= 1:
            return []  # No paragraph breaks found
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            potential_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if len(potential_chunk) <= profile.size:
                current_chunk = potential_chunk
            else:
                # Save current chunk
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Handle large paragraph
                if len(paragraph) <= profile.size:
                    current_chunk = paragraph
                else:
                    # Split large paragraph by sentences
                    large_chunks = self._chunk_by_sentences(paragraph, profile)
                    chunks.extend(large_chunks[:-1])
                    current_chunk = large_chunks[-1] if large_chunks else ""
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def _chunk_by_sentences(self, text: str, profile: ChunkProfile) -> List[str]:
        """Chunk text by sentences with overlap."""
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + profile.size
            
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
                
            start = max(start + len(chunk) - profile.overlap, start + 1)

        return chunks

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
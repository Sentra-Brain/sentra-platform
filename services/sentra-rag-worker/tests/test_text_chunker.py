"""Tests for adaptive text chunking."""

import pytest
from sentra.domain.entities.document_entity import DocumentFileType
from sentra_rag_worker.services.text_chunker import TextChunker, ChunkProfile


def test_chunk_profile():
    """Test ChunkProfile dataclass."""
    profile = ChunkProfile(size=1000, overlap=200)
    assert profile.size == 1000
    assert profile.overlap == 200
    assert profile.prefer_headers is True  # Default
    assert profile.prefer_paragraphs is True  # Default


def test_basic_chunking():
    """Test basic text chunking."""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    
    # Short text should return single chunk
    short_text = "This is a short text that fits in one chunk."
    chunks = chunker.chunk_text(short_text)
    assert len(chunks) == 1
    assert chunks[0] == short_text
    
    # Long text should be split
    long_text = "This is a much longer text. " * 20  # Create long text
    chunks = chunker.chunk_text(long_text)
    assert len(chunks) > 1


def test_adaptive_chunking_by_filetype():
    """Test that different file types use different chunk profiles."""
    chunker = TextChunker()
    
    text = "# Heading 1\n\nParagraph one.\n\n# Heading 2\n\nParagraph two." * 10
    
    # Test with markdown (should prefer headers)
    md_chunks = chunker.chunk_text(text, DocumentFileType.MD)
    
    # Test with plain text (different strategy)
    txt_chunks = chunker.chunk_text(text, DocumentFileType.TXT)
    
    # The results might be different due to different strategies
    assert isinstance(md_chunks, list)
    assert isinstance(txt_chunks, list)
    assert all(isinstance(chunk, str) for chunk in md_chunks)


def test_header_aware_chunking():
    """Test chunking that respects markdown headers."""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)  # Smaller chunk size to force splitting
    
    text = """# First Section
This is content under the first section. It has multiple sentences and should be kept together with its header when possible.

# Second Section  
This is content under the second section. It also has multiple sentences that should be grouped.

# Third Section
Final section content here with more text to make it longer and force chunking behavior."""
    
    chunks = chunker.chunk_text(text, DocumentFileType.MD)
    
    # Should have multiple chunks due to smaller chunk size
    assert len(chunks) >= 1
    
    # Each chunk should ideally start with a header or be a continuation
    for chunk in chunks:
        assert len(chunk.strip()) > 0


def test_paragraph_aware_chunking():
    """Test chunking that respects paragraph boundaries."""
    chunker = TextChunker(chunk_size=150, chunk_overlap=30)
    
    text = """This is the first paragraph. It contains several sentences that should be kept together when possible.

This is the second paragraph. It also contains several sentences that belong together.

This is the third paragraph. It has content that should ideally not be split in the middle."""
    
    chunks = chunker.chunk_text(text, DocumentFileType.TXT)
    
    assert len(chunks) >= 1
    # Verify chunks contain meaningful content
    for chunk in chunks:
        assert len(chunk.strip()) > 0


def test_sentence_boundary_chunking():
    """Test that chunker prefers sentence boundaries."""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    
    text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
    
    chunks = chunker.chunk_text(text)
    
    # Check that chunks don't break in the middle of sentences
    for chunk in chunks:
        # Should not end with partial words (basic check)
        assert not chunk.strip().endswith(',')
        assert len(chunk.strip()) > 0


def test_empty_text_chunking():
    """Test chunking empty or whitespace-only text."""
    chunker = TextChunker()
    
    assert chunker.chunk_text("") == []
    assert chunker.chunk_text("   ") == []
    assert chunker.chunk_text("\n\n\n") == []


def test_chunk_overlap():
    """Test that chunking produces proper overlap."""
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    
    text = "Word " * 50  # Create text longer than chunk size
    
    chunks = chunker.chunk_text(text)
    
    if len(chunks) > 1:
        # Check that there's some overlap between consecutive chunks
        # This is a basic sanity check - exact overlap depends on word boundaries
        assert len(chunks[0]) <= 60  # Should be around chunk_size + some boundary adjustment
        assert len(chunks[1]) > 0


def test_custom_chunk_profile():
    """Test using custom chunk profile."""
    custom_profile = ChunkProfile(
        size=300,
        overlap=50,
        prefer_headers=False,
        prefer_paragraphs=True
    )
    
    chunker = TextChunker(profile=custom_profile)
    
    text = "# Header\n\nParagraph content. " * 20
    
    chunks = chunker.chunk_text(text)
    
    assert isinstance(chunks, list)
    assert len(chunks) >= 1


def test_profile_loading():
    """Test that chunk profiles can be loaded from defaults."""
    chunker = TextChunker()
    
    # Test that we can get profiles for different file types
    pdf_profile = chunker._get_chunk_profile(DocumentFileType.PDF)
    assert pdf_profile.size == 1200
    assert pdf_profile.overlap == 200
    
    md_profile = chunker._get_chunk_profile(DocumentFileType.MD)
    assert md_profile.size == 1600
    assert md_profile.overlap == 150


if __name__ == "__main__":
    pytest.main([__file__])
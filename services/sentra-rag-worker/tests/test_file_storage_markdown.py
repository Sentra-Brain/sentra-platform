import gzip
import hashlib
from uuid import uuid4
from pathlib import Path
from sentra_core.domain.services.file_storage import FileStorageService


def test_save_markdown_gzip_and_sha256(tmp_path):
    # Arrange
    markdown_content = "# Title\n\nSome **markdown** content."
    document_id = uuid4()
    service = FileStorageService(mount_path=str(tmp_path))

    # Act
    relative_path, size, sha256 = service.save_markdown(document_id, markdown_content)

    # Assert
    full_path = tmp_path / relative_path
    assert full_path.exists(), "Markdown file was not created"
    assert full_path.suffix == ".gz", "File should be gzipped"

    # Read and verify gzip content
    with gzip.open(full_path, "rt", encoding="utf-8") as f:
        content = f.read()
    assert content == markdown_content, "Gzipped markdown content mismatch"

    # Verify SHA256
    expected_hash = hashlib.sha256(markdown_content.encode("utf-8")).hexdigest()
    assert sha256 == expected_hash, "SHA256 hash mismatch"

    # ✅ Verify uncompressed size
    expected_size = len(markdown_content.encode("utf-8"))
    assert size == expected_size, f"Expected size {expected_size}, got {size}"

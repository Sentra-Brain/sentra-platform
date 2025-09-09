from uuid import uuid4
from sentra.infra.storage.file_storage import FileStorageService


def test_save_markdown(tmp_path):
    # Arrange
    markdown_content = "# Title\n\nSome **markdown** content."
    document_id = uuid4()
    service = FileStorageService(mount_path=str(tmp_path))

    # Act
    relative_path, size, sha256 = service.save_markdown(document_id, markdown_content)

    # Assert
    full_path = tmp_path / relative_path
    assert full_path.exists(), "Markdown file was not created"
    assert full_path.suffix == ".md", "File should be a markdown"

    # Read and verify markdown content
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert content == markdown_content, "Markdown content mismatch"
    assert size > 0, "File size should be greater than zero"

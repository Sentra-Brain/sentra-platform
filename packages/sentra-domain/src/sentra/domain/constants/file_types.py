# packages/sentra-domain/src/sentra/domain/constants/file_types.py

from sentra.domain.enums.document import DocumentFileType


ALLOWED_FILE_TYPES = {
    ".pdf": DocumentFileType.PDF,
    ".docx": DocumentFileType.DOCX,
    ".txt": DocumentFileType.TXT,
    ".md": DocumentFileType.MD,
}

import os
from sentra_shared.core.logging import get_logger
from sentra_shared.domain.entities.document_entity import DocumentFileType

import chardet
import fitz  # PyMuPDF
import docx2txt
from bs4 import BeautifulSoup
from mailparser import parse_from_file
from ebooklib import epub
import extract_msg

logger = get_logger(__name__)


class DocumentExtractor:
    """Extract clean text content from various document formats."""

    def extract_content(self, filepath: str, filetype: DocumentFileType) -> str:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        try:
            logger.info(f"Extracting content from {filepath} (type: {filetype.value})")

            if filetype in {DocumentFileType.TXT, DocumentFileType.MD}:
                return self._extract_text_file(filepath)
            elif filetype == DocumentFileType.PDF:
                return self._extract_pdf(filepath)
            elif filetype == DocumentFileType.DOCX:
                return self._extract_docx(filepath)
            elif filetype == DocumentFileType.HTML:
                return self._extract_html(filepath)
            elif filetype == DocumentFileType.EML:
                return self._extract_eml(filepath)
            elif filetype == DocumentFileType.MSG:
                return self._extract_msg(filepath)
            elif filetype == DocumentFileType.EPUB:
                return self._extract_epub(filepath)
            else:
                raise ValueError(f"Unsupported file type: {filetype}")

        except Exception as e:
            logger.error(f"Failed to extract content from {filepath}: {e}")
            raise ValueError(f"Content extraction failed: {str(e)}")

    def _extract_text_file(self, filepath: str) -> str:
        with open(filepath, 'rb') as f:
            raw = f.read()
            result = chardet.detect(raw)
            encoding = result['encoding'] or 'utf-8'

        with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
        logger.info(f"Successfully extracted {len(content)} characters from text file")
        return content.strip()

    def _extract_pdf(self, filepath: str) -> str:
        try:
            doc = fitz.open(filepath)
            text = "\n".join(page.get_text() for page in doc)
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text.strip()
        except Exception as e:
            raise ValueError(f"PDF extraction failed: {e}")

    def _extract_docx(self, filepath: str) -> str:
        try:
            text = docx2txt.process(filepath)
            logger.info(f"Extracted {len(text)} characters from DOCX")
            return text.strip()
        except Exception as e:
            raise ValueError(f"DOCX extraction failed: {e}")

    def _extract_html(self, filepath: str) -> str:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'lxml')
            for tag in soup(['script', 'style']):
                tag.decompose()
            text = soup.get_text(separator='\n', strip=True)
            logger.info(f"Extracted {len(text)} characters from HTML")
            return text
        except Exception as e:
            raise ValueError(f"HTML extraction failed: {e}")

    def _extract_eml(self, filepath: str) -> str:
        try:
            mail = parse_from_file(filepath)
            body = mail.body or ''
            logger.info(f"Extracted {len(body)} characters from EML")
            return body.strip()
        except Exception as e:
            raise ValueError(f"EML extraction failed: {e}")

    def _extract_msg(self, filepath: str) -> str:
        try:
            msg = extract_msg.Message(filepath)
            body = msg.body or ''
            logger.info(f"Extracted {len(body)} characters from MSG")
            return body.strip()
        except Exception as e:
            raise ValueError(f"MSG extraction failed: {e}")

    def _extract_epub(self, filepath: str) -> str:
        try:
            book = epub.read_epub(filepath)
            text = ""
            for item in book.get_items():
                if item.get_type() == epub.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'lxml')
                    text += soup.get_text(separator='\n', strip=True) + "\n"
            logger.info(f"Extracted {len(text)} characters from EPUB")
            return text.strip()
        except Exception as e:
            raise ValueError(f"EPUB extraction failed: {e}")

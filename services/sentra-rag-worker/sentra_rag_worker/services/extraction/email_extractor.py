"""Email document extractors for EML and MSG formats."""

import os
from mailparser import parse_from_file
import extract_msg
from sentra_core.core.logging import get_logger
from .base import DocumentExtractorBase, ExtractionPayload

logger = get_logger(__name__)


class EmlExtractor(DocumentExtractorBase):
    """Extract text from EML email files."""
    
    def extract(self, filepath: str) -> ExtractionPayload:
        """Extract content from EML file.
        
        Args:
            filepath: Path to the EML file
            
        Returns:
            ExtractionPayload with email body and headers
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            logger.info(f"Extracting EML content from {filepath}")
            
            # Parse email file
            mail = parse_from_file(filepath)
            
            body = mail.body or ''
            
            # Extract headers
            headers = {
                'from': mail.from_,
                'to': mail.to,
                'subject': mail.subject,
                'date': mail.date,
                'message_id': mail.message_id
            }
            
            # Clean up None values
            headers = {k: v for k, v in headers.items() if v is not None}
            
            logger.info(f"Successfully extracted {len(body)} characters from EML")
            
            return ExtractionPayload(
                raw_text=body.strip(),
                email_headers=headers,
                meta={
                    'format': 'eml',
                    'has_attachments': bool(mail.attachments),
                    'attachment_count': len(mail.attachments) if mail.attachments else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to extract EML content from {filepath}: {e}")
            raise ValueError(f"EML extraction failed: {str(e)}")


class MsgExtractor(DocumentExtractorBase):
    """Extract text from MSG email files."""
    
    def extract(self, filepath: str) -> ExtractionPayload:
        """Extract content from MSG file.
        
        Args:
            filepath: Path to the MSG file
            
        Returns:
            ExtractionPayload with email body and headers
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            logger.info(f"Extracting MSG content from {filepath}")
            
            # Parse MSG file
            msg = extract_msg.Message(filepath)
            
            body = msg.body or ''
            
            # Extract headers
            headers = {
                'from': msg.sender,
                'to': msg.to,
                'subject': msg.subject,
                'date': str(msg.date) if msg.date else None
            }
            
            # Clean up None values
            headers = {k: v for k, v in headers.items() if v is not None}
            
            logger.info(f"Successfully extracted {len(body)} characters from MSG")
            
            return ExtractionPayload(
                raw_text=body.strip(),
                email_headers=headers,
                meta={
                    'format': 'msg',
                    'has_attachments': bool(getattr(msg, 'attachments', None)),
                    'attachment_count': len(getattr(msg, 'attachments', [])) 
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to extract MSG content from {filepath}: {e}")
            raise ValueError(f"MSG extraction failed: {str(e)}")
        finally:
            # Clean up the message object
            try:
                if 'msg' in locals():
                    msg.close()
            except:
                pass
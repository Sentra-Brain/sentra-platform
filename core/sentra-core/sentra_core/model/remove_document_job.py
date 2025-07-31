"""
Schema for document removal job messages.

This defines the message structure for asynchronous document removal jobs
that will be processed by the sentra-rag-worker via RabbitMQ.
"""

from pydantic import BaseModel
from uuid import UUID


class RemoveDocumentJob(BaseModel):
    """
    Schema for document removal job messages.
    
    This job type handles removal of documents from:
    - Vector store (ChromaDB) 
    - File system storage
    - Database status updates
    """
    document_id: UUID
    knowledge_source_id: UUID
    user_id: UUID
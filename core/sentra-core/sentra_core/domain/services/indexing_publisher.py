"""
Unified indexing job publisher service.

This service provides a clean domain-level interface for publishing document 
indexing jobs, abstracting away the low-level AMQP transport details.
"""

import json
from uuid import UUID
import pika
from typing import Dict, Any, List
from sentra_core.core.logging import get_logger
from sentra_core.infra.amqp.rabbitmq_settings import settings

logger = get_logger(__name__)


class IndexingJobPublisher:
    """
    Domain service for publishing document indexing jobs.
    
    This replaces the duplicated publisher files and provides a clean,
    consistent interface for both the API and worker services.
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue = settings.rabbitmq_queue
    
    def connect(self):
        """Establish connection to RabbitMQ server."""
        try:
            credentials = pika.PlainCredentials(
                settings.rabbitmq_user, 
                settings.rabbitmq_password
            )
            parameters = pika.ConnectionParameters(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare the queue (idempotent operation)
            self.channel.queue_declare(queue=self.queue, durable=True)
            
            logger.info(f"Connected to RabbitMQ at {settings.rabbitmq_host}:{settings.rabbitmq_port}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def disconnect(self):
        """Close connection to RabbitMQ server."""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Disconnected from RabbitMQ")
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")
    
    def publish_indexing_job(
        self, 
        document_id: UUID, 
        document_path: str, 
        knowledge_source_id: UUID,
        filename: str = None,
        uploaded_by: str = None
    ) -> bool:
        """
        Publish a single document indexing job.
        
        Args:
            document_id: UUID of the document to index
            document_path: Relative path to the document file
            knowledge_source_id: UUID of the knowledge source
            filename: Original filename (optional)
            uploaded_by: ID of user who uploaded (optional)
            
        Returns:
            True if published successfully, False otherwise
        """
        if not self.channel:
            self.connect()
        
        # Create standardized job message
        job = {
            "document_id": str(document_id),
            "document_path": document_path,
            "knowledge_source_id": str(knowledge_source_id),
            "action": "index_document"
        }
        
        # Add optional fields if provided
        if filename:
            job["filename"] = filename
        if uploaded_by:
            job["uploaded_by"] = uploaded_by
        
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue,
                body=json.dumps(job),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            logger.info(f"Published indexing job for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish indexing job for document {document_id}: {e}")
            return False
    
    def publish_multiple_jobs(self, jobs: List[Dict[str, Any]]) -> int:
        """
        Publish multiple indexing jobs in a batch.
        
        Args:
            jobs: List of job dictionaries with required fields
            
        Returns:
            Number of jobs published successfully
        """
        if not jobs:
            return 0
        
        if not self.channel:
            self.connect()
        
        published_count = 0
        
        for job in jobs:
            # Validate required fields
            required_fields = ['document_id', 'document_path', 'knowledge_source_id']
            if not all(field in job for field in required_fields):
                logger.warning(f"Skipping job with missing fields: {job}")
                continue
            
            # Ensure action field is set
            job.setdefault('action', 'index_document')
            
            try:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.queue,
                    body=json.dumps(job),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Make message persistent
                    )
                )
                published_count += 1
                
            except Exception as e:
                logger.error(f"Failed to publish job {job.get('document_id', 'unknown')}: {e}")
        
        logger.info(f"Published {published_count}/{len(jobs)} indexing jobs")
        return published_count
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Convenience function for backward compatibility
def create_indexing_job(
    document_id: UUID,
    document_path: str, 
    knowledge_source_id: UUID,
    filename: str = None,
    uploaded_by: str = None
) -> Dict[str, Any]:
    """
    Create a standardized indexing job dictionary.
    
    This is useful for services that need to create job objects
    before publishing them.
    """
    job = {
        "document_id": str(document_id),
        "document_path": document_path,
        "knowledge_source_id": str(knowledge_source_id),
        "action": "index_document"
    }
    
    if filename:
        job["filename"] = filename
    if uploaded_by:
        job["uploaded_by"] = uploaded_by
        
    return job
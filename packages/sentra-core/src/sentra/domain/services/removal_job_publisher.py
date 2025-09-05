"""
Document removal job publisher service.

This service provides a clean domain-level interface for publishing document 
removal jobs, following the same pattern as IndexingJobPublisher.
"""

import json
from uuid import UUID
import pika
from typing import Dict, Any, List

from pydantic import BaseModel
from sentra.shared.logging import get_logger
from sentra.infra.amqp.rabbitmq_settings import settings

logger = get_logger(__name__)


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
    
class RemovalJobPublisher:
    """
    Domain service for publishing document removal jobs.
    
    This service handles publishing removal jobs to a dedicated RabbitMQ queue
    separate from the indexing queue for better isolation.
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue = "removal_jobs"  # Dedicated removal queue
    
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
            
            # Declare the removal queue (idempotent operation)
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
    
    def publish_remove_document_job(self, job: RemoveDocumentJob) -> bool:
        """
        Publish a document removal job.
        
        Args:
            job: RemoveDocumentJob instance with document details
            
        Returns:
            True if published successfully, False otherwise
        """
        if not self.channel:
            self.connect()
        
        # Convert Pydantic model to dict for JSON serialization
        job_data = job.model_dump()
        # Convert UUID objects to strings for JSON serialization
        job_data = {k: str(v) if hasattr(v, 'hex') else v for k, v in job_data.items()}
        job_data["action"] = "remove_document"
        
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue,
                body=json.dumps(job_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            logger.info(f"Published removal job for document {job.document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish removal job for document {job.document_id}: {e}")
            return False
    
    def publish_multiple_removal_jobs(self, jobs: List[RemoveDocumentJob]) -> int:
        """
        Publish multiple removal jobs in a batch.
        
        Args:
            jobs: List of RemoveDocumentJob instances
            
        Returns:
            Number of jobs published successfully
        """
        if not jobs:
            return 0
        
        if not self.channel:
            self.connect()
        
        published_count = 0
        
        for job in jobs:
            try:
                if self.publish_remove_document_job(job):
                    published_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to publish removal job {job.document_id}: {e}")
        
        logger.info(f"Published {published_count}/{len(jobs)} removal jobs")
        return published_count
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
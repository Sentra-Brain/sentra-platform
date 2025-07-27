import json
import pika
from typing import Dict, Any

from sentra_shared.core.logging import get_logger
from sentra_shared.infra.amqp.rabbitmq_settings import settings


logger = get_logger(__name__)


class RabbitMQPublisher:
    """Publish indexation jobs to RabbitMQ."""

    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue = settings.rabbitmq_queue

    def connect(self):
        """Establish connection to RabbitMQ server"""
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
        """Close connection to RabbitMQ server"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Disconnected from RabbitMQ")
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")

    def publish_indexation_job(self, job: Dict[str, Any]) -> bool:
        """Publish a document indexation job to the queue.
        
        Args:
            job: Indexation job dictionary
            
        Returns:
            True if published successfully, False otherwise
        """
        if not self.channel:
            self.connect()

        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue,
                body=json.dumps(job),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            logger.info(f"Published indexation job for document {job.get('document_id', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish indexation job: {e}")
            return False

    def publish_multiple_jobs(self, jobs: list) -> int:
        """Publish multiple indexation jobs.
        
        Args:
            jobs: List of indexation job dictionaries
            
        Returns:
            Number of jobs published successfully
        """
        if not jobs:
            return 0
            
        if not self.channel:
            self.connect()

        published_count = 0
        
        for job in jobs:
            if self.publish_indexation_job(job):
                published_count += 1

        logger.info(f"Published {published_count}/{len(jobs)} indexation jobs")
        return published_count

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
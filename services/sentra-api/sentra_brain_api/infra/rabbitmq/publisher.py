# sentra_brain_api/infra/rabbitmq/publisher.py

import json
import pika
from typing import Dict, Any
from sentra_brain_api.crosscutting.logging import get_logger

logger = get_logger(__name__)


class RabbitMQPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None

    def _get_settings(self):
        """Lazy import of settings to avoid circular imports"""
        from sentra_brain_api.core.config import settings
        return settings

    def connect(self):
        """Establish connection to RabbitMQ server"""
        settings = self._get_settings()
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
            self.channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
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

    def publish_indexation_job(self, document_id: str, document_path: str, knowledge_source_id: str):
        """Publish a document indexation job to the queue"""
        settings = self._get_settings()
        if not self.channel:
            self.connect()

        message = {
            "document_id": document_id,
            "document_path": document_path,
            "knowledge_source_id": knowledge_source_id,
            "action": "index_document"
        }

        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=settings.rabbitmq_queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            logger.info(f"Published indexation job for document {document_id}")
        except Exception as e:
            logger.error(f"Failed to publish indexation job for document {document_id}: {e}")
            raise

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


# Singleton instance for dependency injection
_publisher_instance = None

def get_rabbitmq_publisher() -> RabbitMQPublisher:
    global _publisher_instance
    if _publisher_instance is None:
        _publisher_instance = RabbitMQPublisher()
    return _publisher_instance
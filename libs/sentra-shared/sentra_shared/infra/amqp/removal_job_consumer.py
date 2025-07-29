"""
RabbitMQ consumer specifically for document removal jobs.

This consumer handles the removal_jobs queue separately from the indexing queue
to provide better isolation and specific handling for removal operations.
"""

import json
import pika
from typing import Callable, Dict, Any

from sentra_shared.core.logging import get_logger
from sentra_shared.infra.amqp.rabbitmq_settings import settings

logger = get_logger(__name__)


class RemovalJobConsumer:
    """
    RabbitMQ consumer for document removal jobs.
    
    This consumer specifically handles the removal_jobs queue, providing
    dedicated processing for document removal operations.
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue = "removal_jobs"  # Dedicated removal queue
        self.consuming = False

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
            
            # Declare the removal queue (idempotent operation)
            self.channel.queue_declare(queue=self.queue, durable=True)
            
            # Set QoS to process one message at a time
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info(f"Connected to RabbitMQ removal queue at {settings.rabbitmq_host}:{settings.rabbitmq_port}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ for removal jobs: {e}")
            raise

    def disconnect(self):
        """Close connection to RabbitMQ server"""
        try:
            if self.consuming:
                self.channel.stop_consuming()
                self.consuming = False
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Disconnected from RabbitMQ removal queue")
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ removal queue: {e}")

    def start_consuming(self, callback: Callable[[Dict[str, Any]], bool]):
        """Start consuming messages from the removal queue
        
        Args:
            callback: Function that processes the removal message and returns True if successful
        """
        if not self.channel:
            self.connect()

        def message_handler(ch, method, properties, body):
            try:
                # Parse the message
                message = json.loads(body.decode('utf-8'))
                logger.info(f"Received removal message: {message}")
                
                # Process the message
                success = callback(message)
                
                if success:
                    # Acknowledge the message
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"Removal message processed successfully: {message.get('document_id', 'unknown')}")
                else:
                    # For removal jobs, we don't want to retry indefinitely
                    # Acknowledge to prevent reprocessing but log the failure
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.error(f"Removal message processing failed: {message.get('document_id', 'unknown')}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse removal message body: {e}")
                # Reject invalid messages without requeue
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Unexpected error processing removal message: {e}")
                # Acknowledge to prevent infinite reprocessing
                ch.basic_ack(delivery_tag=method.delivery_tag)

        # Set up the consumer
        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=message_handler
        )

        logger.info(f"Starting to consume removal messages from queue: {self.queue}")
        self.consuming = True
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping removal consumer...")
            self.channel.stop_consuming()
            self.consuming = False
        except Exception as e:
            logger.error(f"Error during removal message consumption: {e}")
            self.consuming = False
            raise

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
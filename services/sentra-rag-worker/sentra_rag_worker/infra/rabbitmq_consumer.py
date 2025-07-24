import json
import pika
from typing import Callable, Dict, Any
from sentra_rag_worker.core.config import settings
from sentra_rag_worker.core.logging import get_logger

logger = get_logger(__name__)


class RabbitMQConsumer:
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
            
            # Set QoS to process one message at a time
            self.channel.basic_qos(prefetch_count=1)
            
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

    def start_consuming(self, callback: Callable[[Dict[str, Any]], bool]):
        """Start consuming messages from the queue
        
        Args:
            callback: Function that processes the message and returns True if successful
        """
        if not self.channel:
            self.connect()

        def message_handler(ch, method, properties, body):
            try:
                # Parse the message
                message = json.loads(body.decode('utf-8'))
                logger.info(f"Received message: {message}")
                
                # Process the message
                success = callback(message)
                
                if success:
                    # Acknowledge the message
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"Message processed successfully: {message.get('document_id', 'unknown')}")
                else:
                    # Reject and requeue the message
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    logger.warning(f"Message processing failed, requeuing: {message.get('document_id', 'unknown')}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse message body: {e}")
                # Reject invalid messages without requeue
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except Exception as e:
                logger.error(f"Unexpected error processing message: {e}")
                # Reject and requeue for potential retry
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        # Set up the consumer
        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=message_handler
        )

        logger.info(f"Starting to consume messages from queue: {self.queue}")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping consumer...")
            self.channel.stop_consuming()
            self.disconnect()
        except Exception as e:
            logger.error(f"Error during message consumption: {e}")
            raise

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
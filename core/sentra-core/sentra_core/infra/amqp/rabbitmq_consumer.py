import aio_pika
import asyncio
import json
from typing import Callable, Dict, Any, Awaitable

from sentra_core.logging import get_logger
from sentra_core.infra.amqp.rabbitmq_settings import settings

logger = get_logger(__name__)


class RabbitMQConsumer:
    def __init__(self):
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.abc.AbstractChannel | None = None
        self.queue_name = settings.rabbitmq_queue

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                login=settings.rabbitmq_user,
                password=settings.rabbitmq_password
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)

            logger.info(f"Connected to RabbitMQ at {settings.rabbitmq_host}:{settings.rabbitmq_port}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self):
        try:
            if self.connection:
                await self.connection.close()
                logger.info("Disconnected from RabbitMQ")
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")

    async def start_consuming(self, callback: Callable[[Dict[str, Any]], Awaitable[bool]]):
        if not self.channel:
            await self.connect()

        queue = await self.channel.declare_queue(self.queue_name, durable=True)

        logger.info(f"Starting to consume messages from queue: {self.queue_name}")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    payload = json.loads(message.body.decode("utf-8"))
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON: {e}")
                    await message.reject(requeue=False)  # No need to requeue invalid messages
                    continue

                try:
                    logger.info(f"📥 Received message: {payload}")
                    async with message.process():  # Then, yes, process the message
                        await callback(payload)
                        logger.info(f"✅ Message processed successfully: {payload.get('document_id', 'unknown')}")
                except Exception as e:
                    logger.error(f"❌ Failed to process message: {e}")
                    try:
                        await message.ack()  # Avoid infinite requeue
                        logger.warning("⚠️ Message manually acked after exception")
                    except Exception as ack_err:
                        logger.error(f"❌ Failed to manually ack: {ack_err}")


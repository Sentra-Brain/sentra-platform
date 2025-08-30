#!/usr/bin/env python3

import asyncio
import json
import os
import signal
import sys
import uuid
from typing import List, Dict, Any, Optional

from sentra_core.domain.repository.document_repository import DocumentRepository
from sentra_rag_worker.core.config import settings
from sentra_rag_worker.services.document_processor import DocumentProcessor
from sentra_rag_worker.services.folder_scanner import FolderScanner
from sentra_core.logging import get_logger, configure_logging
from sentra_core.domain.repository.knowledge_source_repository import KnowledgeSourceRepository
from sentra_core.domain.services.indexing_publisher import IndexingJobPublisher
# from sentra_rag_worker.core.observability import instrument_worker, trace_job_processing, get_correlation_id_from_message
from sentra_core.infra.amqp.rabbitmq_consumer import RabbitMQConsumer  # ya usando aio-pika
from sentra_core.infra.sql.postgres_service import create_db_session

debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
configure_logging(debug=debug_mode)
logger = get_logger("sentra_rag_worker.main")


class RAGWorker:
    def __init__(self):
        self.indexing_consumer = RabbitMQConsumer()
        self.document_processor = DocumentProcessor()
        self.publisher = IndexingJobPublisher()
        self.running = False
        self._folder_scan_task = None

    async def start(self):
        logger.info("Starting sentra-rag-worker...")
        self.running = True

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self._folder_scan_task = asyncio.create_task(self._folder_scan_loop())
        await self.indexing_consumer.start_consuming(self._process_indexing_message_linear)

    async def stop(self):
        logger.info("Stopping sentra-rag-worker...")
        self.running = False

        if self._folder_scan_task:
            self._folder_scan_task.cancel()
            try:
                await self._folder_scan_task
            except asyncio.CancelledError:
                pass

        await self.indexing_consumer.disconnect()
        self.publisher.disconnect()
        logger.info("sentra-rag-worker stopped")

    def _signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False

    async def _process_indexing_message_linear(self, message: Dict[str, Any]) -> bool:
        try:
            required = ['document_id', 'document_path', 'knowledge_source_id']
            if missing := [k for k in required if k not in message]:
                logger.error(f"Missing fields: {missing}")
                return True

            path = message["document_path"]
            filename = message.get("filename") or os.path.basename(path)
            ext = os.path.splitext(filename)[1].lower().lstrip('.')
            if ext not in {"pdf", "docx", "txt", "md"}:
                logger.error(f"Unsupported filetype: {filename}")
                return True

            enriched = {
                "document_id": message["document_id"],
                "knowledge_source_id": message["knowledge_source_id"],
                "filepath": path,
                "filename": filename,
                "filetype": ext,
                "display_name": filename,
                "uploaded_by": message.get("uploaded_by"),
                "request_id": message.get("request_id", str(uuid.uuid4()))
            }

            success = await self.document_processor.process_document(enriched)
            logger.info(
                f"{'✅' if success else '❌'} Document {message['document_id']} processed"
            )
            return True
        except Exception as e:
            logger.error(f"Fatal error in message processing: {e}")
            return True

    async def _folder_scan_loop(self):
        logger.info(f"🔍 Starting folder scan every {settings.folder_scan_interval}s")
        while self.running:
            try:
                await asyncio.sleep(settings.folder_scan_interval)
                await self._perform_folder_scan()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in folder scan loop: {e}")
                await asyncio.sleep(5)

    async def _perform_folder_scan(self):
        db = create_db_session()
        try:
            logger.info("🔍 Scanning folder sources for new files")
            knowledge_source_repo = KnowledgeSourceRepository(db)
            document_repo = DocumentRepository(db)
            scanner = FolderScanner(knowledge_source_repo, document_repo)

            new_jobs = scanner.scan_folder_sources()
            if new_jobs:
                with self.publisher:
                    count = self.publisher.publish_multiple_jobs(new_jobs)
                    logger.info(f"📤 Published {count} new jobs")

            missing = scanner.detect_missing_files()
            if missing:
                marked = scanner.mark_missing_files_as_failed(missing)
                logger.info(f"🚫 Marked {marked} missing files as failed")
        except Exception as e:
            logger.error(f"Error during folder scan: {e}")
        finally:
            db.close()


async def main():
    if debug_mode:
        logger.info("✅ Debug mode enabled: waiting for debugger on port 5679")
        import debugpy
        debugpy.listen(("0.0.0.0", 5679))
        debugpy.wait_for_client()
        logger.info("✅ Debugger attached")

    logger.info("🚀 Starting sentra-rag-worker...")
    logger.info(f"📡 RabbitMQ: {settings.rabbitmq_host}:{settings.rabbitmq_port}")
    logger.info(f"📚 ChromaDB: {settings.chroma_url}")
    logger.info(f"🕐 Scan interval: {settings.folder_scan_interval}s")

    worker = RAGWorker()
    try:
        await worker.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await worker.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


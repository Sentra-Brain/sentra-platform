#!/usr/bin/env python3

from sentra_rag_worker.core.config import settings
from sentra_rag_worker.core.observability import instrument_worker, trace_job_processing, get_correlation_id_from_message
from sentra_rag_worker.services.document_processor import DocumentProcessor
from sentra_rag_worker.services.folder_scanner import FolderScanner
from sentra_shared.core.logging import get_logger, set_request_id
from sentra_shared.domain.repositories.knowledge_repository import KnowledgeRepository
from sentra_shared.domain.services.indexing_publisher import IndexingJobPublisher
from sentra_shared.infra.amqp.rabbitmq_consumer import RabbitMQConsumer
from sentra_shared.infra.sql import postgres_service
from sentra_shared.infra.sql.postgres_service import create_db_session
from typing import Dict, Any
import asyncio
import os
import signal
import sys
import uuid

logger = get_logger("sentra_rag_worker.main")


class RAGWorker:
    """Main RAG worker application."""

    def __init__(self):
        self.consumer = RabbitMQConsumer()
        self.publisher = IndexingJobPublisher()
        self.document_processor = DocumentProcessor()
        self.running = False
        self._folder_scan_task = None

    async def start(self):
        """Start the RAG worker."""
        logger.info("Starting sentra-rag-worker...")
        
        # Setup observability
        instrument_worker()
        
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Start folder scanning task
        self._folder_scan_task = asyncio.create_task(self._folder_scan_loop())
        
        # Start consuming messages with linear processing
        try:
            logger.info("Starting linear message processing...")
            self.consumer.start_consuming(self._process_message_linear)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error in message consumption: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the RAG worker gracefully."""
        logger.info("Stopping sentra-rag-worker...")
        
        self.running = False
        
        # Cancel folder scan task
        if self._folder_scan_task:
            self._folder_scan_task.cancel()
            try:
                await self._folder_scan_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect from services
        self.consumer.disconnect()
        self.publisher.disconnect()
        
        logger.info("sentra-rag-worker stopped")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False

    def _process_message_linear(self, message: Dict[str, Any]) -> bool:
        """
        Process message with linear flow: validate → process → acknowledge.
        No retries, no requeueing. Process once and mark done.
        """
        try:
            # Validate required fields
            required_fields = ['document_id', 'document_path', 'knowledge_source_id']
            missing_fields = [f for f in required_fields if f not in message]

            if missing_fields:
                logger.error(f"Message missing required fields: {missing_fields}")
                return True  # Acknowledge to prevent reprocessing

            # Extract and enrich message data
            document_path = message['document_path']
            filename = message.get('filename') or os.path.basename(document_path)
            
            # Determine file type from path
            extension = os.path.splitext(filename)[1].lower().lstrip('.')
            filetype = extension if extension in ['pdf', 'docx', 'txt', 'md'] else None

            if not filetype:
                logger.error(f"Unsupported or missing filetype for file: {filename}")
                return True  # Acknowledge to prevent reprocessing

            # Create standardized processing message
            processing_message = {
                "document_id": message['document_id'],
                "knowledge_source_id": message['knowledge_source_id'],
                "filepath": document_path,  # Will be resolved to absolute path in processor
                "filename": filename,
                "filetype": filetype,
                "display_name": filename,
                "uploaded_by": message.get("uploaded_by"),
                "request_id": message.get("request_id", str(uuid.uuid4()))  # Ensure request_id is set
            }

            # Process document (handles all errors internally)
            success = self.document_processor.process_document(processing_message)
            
            # Always acknowledge - no retries
            if success:
                logger.info(f"Successfully processed document {message['document_id']}")
            else:
                logger.error(f"Failed to process document {message['document_id']} - marked as failed")
            
            return True  # Always acknowledge

        except Exception as e:
            logger.error(f"Unexpected error processing message: {e}")
            return True  # Acknowledge even on unexpected errors to prevent infinite reprocessing

    async def _folder_scan_loop(self):
        """Periodic folder scanning loop."""
        logger.info(f"Starting folder scan loop (interval: {settings.folder_scan_interval}s)")
        
        while self.running:
            try:
                await asyncio.sleep(settings.folder_scan_interval)
                
                if not self.running:
                    break
                
                logger.info("Performing folder scan...")
                await self._perform_folder_scan()
                
            except asyncio.CancelledError:
                logger.info("Folder scan loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in folder scan loop: {e}")
                # Continue the loop even if scan fails
                await asyncio.sleep(5)  # Short delay before retry

    async def _perform_folder_scan(self):
        """Perform a single folder scan."""
        db = None
        try:
            # Create database session
            db = create_db_session()
            repo = KnowledgeRepository(db)
            scanner = FolderScanner(repo)
            
            # Scan for new files
            new_jobs = scanner.scan_folder_sources()
            
            # Publish new indexation jobs
            if new_jobs:
                with self.publisher:
                    published = self.publisher.publish_multiple_jobs(new_jobs)
                    logger.info(f"Published {published} new indexation jobs from folder scan")
            
            # Detect and mark missing files
            missing_docs = scanner.detect_missing_files()
            if missing_docs:
                marked = scanner.mark_missing_files_as_failed(missing_docs)
                logger.info(f"Marked {marked} missing files as failed")
            
        except Exception as e:
            logger.error(f"Error during folder scan: {e}")
        finally:
            if db:
                db.close()


async def main():
    """Main entry point."""
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"

    if debug_mode:
        logger.info("✅ Debug mode enabled: waiting for debugger on port 5679")
        import debugpy
        debugpy.listen(("0.0.0.0", 5679))
        debugpy.wait_for_client()
        logger.info("✅ Debugger attached")

    logger.info("sentra-rag-worker starting...")
    logger.info(f"Configuration: RabbitMQ={settings.rabbitmq_host}:{settings.rabbitmq_port}, ")
    logger.info(f"ChromaDB={settings.chroma_url}, ")
    logger.info(f"Scan interval={settings.folder_scan_interval}s")

    worker = RAGWorker()

    
    postgres_service.init_db()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
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
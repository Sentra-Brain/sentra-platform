#!/usr/bin/env python3


from sentra_rag_worker.core.config import settings
from sentra_rag_worker.core.observability import instrument_worker, trace_job_processing, get_correlation_id_from_message
from sentra_rag_worker.services.document_processor import DocumentProcessor
from sentra_rag_worker.services.document_removal_processor import DocumentRemovalProcessor
from sentra_rag_worker.services.folder_scanner import FolderScanner
from sentra_core.core.logging import get_logger, configure_logging
from sentra_core.domain.repository.knowledge_source_repository import KnowledgeRepository
from sentra_core.domain.services.indexing_publisher import IndexingJobPublisher
from sentra_core.infra.amqp.rabbitmq_consumer import RabbitMQConsumer
from sentra_core.infra.amqp.removal_job_consumer import RemovalJobConsumer
from sentra_core.infra.sql import postgres_service
from sentra_core.infra.sql.postgres_service import create_db_session
from typing import Dict, Any
import asyncio
import os
import signal
import sys
import uuid


debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
configure_logging(debug=debug_mode)
logger = get_logger("sentra_rag_worker.main")


class RAGWorker:
    """Main RAG worker application."""

    def __init__(self):
        self.indexing_consumer = RabbitMQConsumer()
        self.removal_consumer = RemovalJobConsumer()
        self.publisher = IndexingJobPublisher()
        self.document_processor = DocumentProcessor()
        self.removal_processor = DocumentRemovalProcessor()
        self.running = False
        self._folder_scan_task = None
        self._removal_consumer_task = None

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
        
        # Start removal consumer task
        self._removal_consumer_task = asyncio.create_task(self._removal_consumer_loop())
        
        # Start consuming indexing messages with linear processing (main thread)
        try:
            logger.info("Starting linear message processing for indexing jobs...")
            self.indexing_consumer.start_consuming(self._process_indexing_message_linear)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error in indexing message consumption: {e}")
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
        
        # Cancel removal consumer task
        if self._removal_consumer_task:
            self._removal_consumer_task.cancel()
            try:
                await self._removal_consumer_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect from services
        self.indexing_consumer.disconnect()
        self.removal_consumer.disconnect()
        self.publisher.disconnect()
        
        logger.info("sentra-rag-worker stopped")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False

    def _process_indexing_message_linear(self, message: Dict[str, Any]) -> bool:
        """
        Process indexing message with linear flow: validate → process → acknowledge.
        No retries, no requeueing. Process once and mark done.
        """
        try:
            # Validate required fields
            required_fields = ['document_id', 'document_path', 'knowledge_source_id']
            missing_fields = [f for f in required_fields if f not in message]

            if missing_fields:
                logger.error(f"Indexing message missing required fields: {missing_fields}")
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
                logger.info(f"Successfully processed indexing document {message['document_id']}")
            else:
                logger.error(f"Failed to process indexing document {message['document_id']} - marked as failed")
            
            return True  # Always acknowledge

        except Exception as e:
            logger.error(f"Unexpected error processing indexing message: {e}")
            return True  # Acknowledge even on unexpected errors to prevent infinite reprocessing

    def _process_removal_message(self, message: Dict[str, Any]) -> bool:
        """
        Process removal message.
        """
        try:
            # Validate required fields
            required_fields = ['document_id', 'knowledge_source_id', 'user_id']
            missing_fields = [f for f in required_fields if f not in message]

            if missing_fields:
                logger.error(f"Removal message missing required fields: {missing_fields}")
                return True  # Acknowledge to prevent reprocessing

            # Process document removal (handles all errors internally)
            success = self.removal_processor.process_removal_job(message)
            
            if success:
                logger.info(f"Successfully processed removal for document {message['document_id']}")
            else:
                logger.error(f"Failed to process removal for document {message['document_id']}")
            
            return True  # Always acknowledge removal jobs

        except Exception as e:
            logger.error(f"Unexpected error processing removal message: {e}")
            return True  # Acknowledge even on unexpected errors

    async def _removal_consumer_loop(self):
        """Run the removal consumer in a separate task."""
        logger.info("Starting removal consumer loop...")
        
        while self.running:
            try:
                # Start consuming removal messages
                logger.info("Starting removal message consumer...")
                self.removal_consumer.start_consuming(self._process_removal_message)
                
            except Exception as e:
                logger.error(f"Error in removal consumer: {e}")
                if self.running:
                    logger.info("Restarting removal consumer in 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    break
        
        logger.info("Removal consumer loop stopped")

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
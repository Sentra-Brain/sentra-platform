#!/usr/bin/env python3

import asyncio
import signal
import os
import sys
from typing import Dict, Any
from sentra_shared.core.logging import get_logger
from sentra_rag_worker.core.config import settings
from sentra_rag_worker.infra.database import create_db_session
from sentra_rag_worker.infra.knowledge_repository import KnowledgeRepository
from sentra_rag_worker.infra.rabbitmq_consumer import RabbitMQConsumer
from sentra_rag_worker.infra.rabbitmq_publisher import RabbitMQPublisher
from sentra_rag_worker.features.document_processor import DocumentProcessor
from sentra_rag_worker.features.folder_scanner import FolderScanner

logger = get_logger("sentra_rag_worker.main")


class RAGWorker:
    """Main RAG worker application."""

    def __init__(self):
        self.consumer = RabbitMQConsumer()
        self.publisher = RabbitMQPublisher()
        self.document_processor = DocumentProcessor()
        self.running = False
        self._folder_scan_task = None

    async def start(self):
        """Start the RAG worker."""
        logger.info("Starting sentra-rag-worker...")
        
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Start folder scanning task
        self._folder_scan_task = asyncio.create_task(self._folder_scan_loop())
        
        # Start consuming messages
        try:
            logger.info("Starting message consumption...")
            self.consumer.start_consuming(self._process_message)
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
        # Note: The consumer will handle the actual shutdown in its main loop

    def _process_message(self, message: Dict[str, Any]) -> bool:
        try:
            required_fields = ['document_id', 'document_path', 'knowledge_source_id']
            missing_fields = [f for f in required_fields if f not in message]

            if missing_fields:
                logger.error(f"Message missing required fields: {missing_fields}")
                return False

            # Adapt message format to expected fields
            document_path = message['document_path']
            filename = os.path.basename(document_path)
            extension = os.path.splitext(filename)[1].lower().lstrip('.')
            filetype = extension if extension in ['pdf', 'docx', 'txt', 'md'] else None

            if not filetype:
                logger.error(f"Unsupported or missing filetype for file: {filename}")
                return False

            enriched_message = {
                "document_id": message['document_id'],
                "knowledge_source_id": message['knowledge_source_id'],
                "filepath": document_path,
                "filename": filename,
                "filetype": filetype,
                # Optional:
                "display_name": filename,
                "uploaded_by": message.get("uploaded_by")  # if present
            }

            return self.document_processor.process_document(enriched_message)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False

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
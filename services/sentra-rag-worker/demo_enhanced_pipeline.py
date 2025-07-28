#!/usr/bin/env python3
"""
Demo script showing the enhanced document processing pipeline.
This simulates what would happen when a document is processed.
"""

import sys
import os
import time
from uuid import uuid4

# Set test environment variables
os.environ.update({
    'DATABASE_URL': 'sqlite:///./test.db',
    'RABBITMQ_HOST': 'localhost',
    'RABBITMQ_PORT': '5672',
    'RABBITMQ_USER': 'guest',
    'RABBITMQ_PASSWORD': 'guest',
    'RABBITMQ_QUEUE': 'test_queue',
    'CHROMA_URL': 'http://localhost:8000',
    'KNOWLEDGE_ROOT': '/tmp/test_knowledge',
    'FOLDER_SCAN_INTERVAL': '60',
    'EMBEDDING_MODEL': 'BAAI/bge-small-en-v1.5',
    'CHUNK_SIZE': '100',
    'CHUNK_OVERLAP': '20'
})

# Add the project root to the path
sys.path.insert(0, '/home/runner/work/sentra-brain/sentra-brain/services/sentra-rag-worker')


def demo_enhanced_logging():
    """Demonstrate the enhanced logging capabilities."""
    print("🚀 Enhanced Document Processing Pipeline Demo")
    print("=" * 60)
    
    from sentra_shared.core.logging import get_logger, set_request_id, StepTimer, configure_logging
    from sentra_shared.domain.entities.document_entity import DocumentStatus
    
    # Configure logging
    configure_logging(debug=True)
    
    # Set up request context
    request_id = set_request_id("demo-request-12345")
    logger = get_logger("demo_processor")
    
    document_id = str(uuid4())
    
    print(f"📋 Processing document {document_id}")
    print(f"🔗 Request ID: {request_id}")
    print()
    
    # Simulate the document processing pipeline
    statuses = [
        (DocumentStatus.PENDING, "Document queued for processing"),
        (DocumentStatus.PROCESSING, "Starting document processing"),
        (DocumentStatus.EXTRACTING, "Extracting content from document"),
        (DocumentStatus.CHUNKING, "Splitting content into chunks"),
        (DocumentStatus.EMBEDDING, "Generating embeddings for chunks"),
        (DocumentStatus.INDEXING, "Indexing chunks into vector database"),
        (DocumentStatus.INDEXED, "Successfully indexed document")
    ]
    
    for i, (status, message) in enumerate(statuses):
        print(f"📊 Step {i+1}/7: {status.value.upper()}")
        
        # Log the status update
        logger.info_step(f"status_update", 
                        document_id=document_id, 
                        status=status.value,
                        status_message=message)
        
        # Simulate work being done with timing
        step_name = status.value
        with StepTimer(logger, step_name, document_id):
            # Simulate processing time
            if status == DocumentStatus.EXTRACTING:
                time.sleep(0.2)  # Extraction takes longer
            elif status == DocumentStatus.EMBEDDING:
                time.sleep(0.3)  # Embedding takes the longest
            else:
                time.sleep(0.1)  # Other steps are faster
        
        print(f"   ✓ {message}")
        print()
    
    # Show error handling
    print("🚨 Error Handling Demo")
    print("-" * 30)
    
    try:
        with StepTimer(logger, "simulated_failure", document_id):
            # Simulate a failure
            raise Exception("ChromaDB connection timeout")
    except Exception as e:
        logger.error_step("processing_failed", 
                         document_id=document_id, 
                         error=str(e),
                         status="FAILED")
        print(f"   ❌ Error logged: {e}")
    
    print()
    print("✅ Demo completed! Enhanced logging provides:")
    print("   • Request ID correlation across all log entries")
    print("   • Structured logging with document_id, step, duration")
    print("   • Automatic timing for each processing step")
    print("   • Clear error messages with context")
    print("   • Status updates at each pipeline stage")


def demo_status_flow():
    """Demonstrate the new document status flow."""
    print("\n🔄 Document Status Flow Demo")
    print("=" * 60)
    
    from sentra_shared.domain.entities.document_entity import DocumentStatus
    
    print("New Enhanced Status Flow:")
    print()
    
    statuses = [
        DocumentStatus.PENDING,
        DocumentStatus.PROCESSING,
        DocumentStatus.EXTRACTING,
        DocumentStatus.CHUNKING,
        DocumentStatus.EMBEDDING,
        DocumentStatus.INDEXING,
        DocumentStatus.INDEXED
    ]
    
    for i, status in enumerate(statuses):
        if i > 0:
            print("    ↓")
        print(f"  {status.value.upper()}")
    
    print()
    print("Benefits:")
    print("  • Frontend can show detailed progress")
    print("  • Better debugging of failed documents")
    print("  • Users know exactly what's happening")
    print("  • Fail-fast with clear error messages")


if __name__ == "__main__":
    try:
        demo_status_flow()
        demo_enhanced_logging()
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
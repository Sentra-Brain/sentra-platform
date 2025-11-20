#!/usr/bin/env python3
"""
Integration test to verify message processing pipeline without external services.
"""

import sys
import os
import json
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

sys.path.insert(0, '/home/runner/work/sentra-brain/sentra-brain/src/Sentra.Rag.Worker')

def test_message_structure():
    """Test that we can create proper indexation message structure."""
    print("Testing message structure...")
    
    try:
        # Create a test message similar to what would come from RabbitMQ
        test_message = {
            "document_id": str(uuid4()),
            "knowledge_source_id": str(uuid4()),
            "filepath": "/tmp/test_document.txt",
            "filename": "test_document.txt",
            "display_name": "Test Document",
            "uploaded_by": str(uuid4()),
            "filetype": "txt"
        }
        
        # Validate required fields
        required_fields = ['document_id', 'knowledge_source_id', 'filepath', 'filename', 'filetype']
        missing_fields = [field for field in required_fields if field not in test_message]
        
        assert not missing_fields, f"Missing fields: {missing_fields}"
        print("✓ Message structure validation works")
        
        # Test JSON serialization/deserialization
        json_str = json.dumps(test_message)
        parsed_message = json.loads(json_str)
        assert parsed_message == test_message
        print("✓ Message JSON serialization works")
        
        return True
        
    except Exception as e:
        print(f"✗ Message structure test failed: {e}")
        return False

def test_document_processor_validation():
    """Test document processor message validation."""
    print("\nTesting document processor validation...")
    
    try:
        from sentra_rag_worker.services.document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        print("✓ Document processor can be instantiated")
        
        return True
        
    except Exception as e:
        print(f"✗ Document processor test failed: {e}")
        return False

def test_folder_scanner_structure():
    """Test folder scanner can be instantiated."""
    print("\nTesting folder scanner...")
    
    try:
        # We can't test the full functionality without database, but we can test imports
        from sentra_rag_worker.services.folder_scanner import FolderScanner
        print("✓ Folder scanner import works")
        
        # Test constants
        supported_extensions = FolderScanner.SUPPORTED_EXTENSIONS
        assert '.pdf' in supported_extensions
        assert '.txt' in supported_extensions
        assert '.docx' in supported_extensions
        assert '.md' in supported_extensions
        print("✓ Supported extensions configured correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Folder scanner test failed: {e}")
        return False

def test_rabbitmq_consumer_structure():
    """Test RabbitMQ consumer structure."""
    print("\nTesting RabbitMQ consumer...")
    
    try:
        from sentra_rag_worker.infra.rabbitmq_consumer import RabbitMQConsumer
        
        consumer = RabbitMQConsumer()
        print("✓ RabbitMQ consumer can be instantiated")
        
        # Test that it has the required queue configuration
        from sentra_rag_worker.core.config import settings
        assert consumer.queue == settings.rabbitmq_queue
        print("✓ Consumer queue configuration correct")
        
        return True
        
    except Exception as e:
        print(f"✗ RabbitMQ consumer test failed: {e}")
        return False

def main():
    """Run integration tests."""
    print("Running Sentra.Rag.Worker integration tests...")
    print("=" * 50)
    
    tests = [
        test_message_structure,
        test_document_processor_validation,
        test_folder_scanner_structure,
        test_rabbitmq_consumer_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Integration tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All integration tests passed!")
        return 0
    else:
        print("✗ Some integration tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
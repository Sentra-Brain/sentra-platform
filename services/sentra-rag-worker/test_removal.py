#!/usr/bin/env python3
"""
Test document removal functionality.
"""

import sys
import os
import tempfile
from pathlib import Path
from uuid import uuid4

# Set test environment variables before importing anything
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
sys.path.insert(0, '/home/runner/work/sentra-brain/sentra-brain/core/sentra-core')

def test_removal_job_schema():
    """Test the RemoveDocumentJob schema."""
    print("Testing RemoveDocumentJob schema...")
    
    try:
        from sentra_core.model.remove_document_job import RemoveDocumentJob
        
        # Create a test job
        job = RemoveDocumentJob(
            document_id=uuid4(),
            knowledge_source_id=uuid4(),
            user_id=uuid4()
        )
        
        # Test serialization
        job_dict = job.model_dump()
        assert 'document_id' in job_dict
        assert 'knowledge_source_id' in job_dict
        assert 'user_id' in job_dict
        
        print("✓ RemoveDocumentJob schema works")
        return True
        
    except Exception as e:
        print(f"✗ RemoveDocumentJob schema test failed: {e}")
        return False

def test_document_status_enum():
    """Test the updated DocumentStatus enum."""
    print("\nTesting DocumentStatus enum...")
    
    try:
        from sentra_core.domain.enums.document import DocumentStatus
        
        # Check that new statuses exist
        assert hasattr(DocumentStatus, 'TO_BE_REMOVED')
        assert hasattr(DocumentStatus, 'REMOVED')
        
        # Check values
        assert DocumentStatus.TO_BE_REMOVED.value == "to_be_removed"
        assert DocumentStatus.REMOVED.value == "removed"
        
        # Check that all expected statuses exist
        expected_statuses = [
            'PENDING', 'PROCESSING', 'EXTRACTING', 'CHUNKING', 
            'EMBEDDING', 'INDEXING', 'INDEXED', 'FAILED',
            'TO_BE_REMOVED', 'REMOVED'
        ]
        
        for status in expected_statuses:
            assert hasattr(DocumentStatus, status)
        
        print("✓ DocumentStatus enum updated correctly")
        return True
        
    except Exception as e:
        print(f"✗ DocumentStatus enum test failed: {e}")
        return False

def test_removal_publisher_import():
    """Test that RemovalJobPublisher can be imported."""
    print("\nTesting RemovalJobPublisher import...")
    
    try:
        from sentra_core.domain.services.removal_job_publisher import RemovalJobPublisher
        
        # Test instantiation (without connecting)
        publisher = RemovalJobPublisher()
        assert publisher.queue == "removal_jobs"
        
        print("✓ RemovalJobPublisher imports and instantiates correctly")
        return True
        
    except Exception as e:
        print(f"✗ RemovalJobPublisher import test failed: {e}")
        return False

def test_removal_consumer_import():
    """Test that RemovalJobConsumer can be imported."""
    print("\nTesting RemovalJobConsumer import...")
    
    try:
        from sentra_core.infra.amqp.removal_job_consumer import RemovalJobConsumer
        
        # Test instantiation (without connecting)
        consumer = RemovalJobConsumer()
        assert consumer.queue == "removal_jobs"
        
        print("✓ RemovalJobConsumer imports and instantiates correctly")
        return True
        
    except Exception as e:
        print(f"✗ RemovalJobConsumer import test failed: {e}")
        return False

def test_removal_processor_import():
    """Test that DocumentRemovalProcessor can be imported."""
    print("\nTesting DocumentRemovalProcessor import...")
    
    try:
        from sentra_rag_worker.services.document_removal_processor import DocumentRemovalProcessor
        
        # Test instantiation (without connecting to external services)
        processor = DocumentRemovalProcessor()
        assert processor is not None
        
        print("✓ DocumentRemovalProcessor imports and instantiates correctly")
        return True
        
    except Exception as e:
        print(f"✗ DocumentRemovalProcessor import test failed: {e}")
        return False

def test_removal_job_serialization():
    """Test RemoveDocumentJob JSON serialization for RabbitMQ."""
    print("\nTesting RemoveDocumentJob JSON serialization...")
    
    try:
        from sentra_core.model.remove_document_job import RemoveDocumentJob
        import json
        
        # Create a test job
        job = RemoveDocumentJob(
            document_id=uuid4(),
            knowledge_source_id=uuid4(),
            user_id=uuid4()
        )
        
        # Convert to dict (as RemovalJobPublisher would)
        job_data = job.model_dump()
        # Convert UUID objects to strings for JSON serialization
        job_data = {k: str(v) if hasattr(v, 'hex') else v for k, v in job_data.items()}
        job_data["action"] = "remove_document"
        
        # Test JSON serialization
        json_str = json.dumps(job_data)
        assert "remove_document" in json_str
        
        # Test deserialization
        parsed = json.loads(json_str)
        assert parsed["action"] == "remove_document"
        assert "document_id" in parsed
        
        print("✓ RemoveDocumentJob JSON serialization works")
        return True
        
    except Exception as e:
        print(f"✗ RemoveDocumentJob JSON serialization test failed: {e}")
        return False

def main():
    """Run all removal functionality tests."""
    print("Running document removal functionality tests...")
    print("=" * 60)
    
    tests = [
        test_removal_job_schema,
        test_document_status_enum,
        test_removal_publisher_import,
        test_removal_consumer_import,
        test_removal_processor_import,
        test_removal_job_serialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"Document removal tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All removal functionality tests passed!")
        return 0
    else:
        print("✗ Some removal functionality tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
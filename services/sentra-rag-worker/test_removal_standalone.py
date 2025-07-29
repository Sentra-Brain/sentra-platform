#!/usr/bin/env python3
"""
Standalone test for document removal functionality without external dependencies.
"""

import sys
import os
import tempfile
import json
from pathlib import Path
from uuid import uuid4
from unittest.mock import Mock, patch, MagicMock

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

# Add project paths
sys.path.insert(0, '/home/runner/work/sentra-brain/sentra-brain/services/sentra-rag-worker')
sys.path.insert(0, '/home/runner/work/sentra-brain/sentra-brain/libs/sentra-shared')

def test_removal_schemas_and_publishers():
    """Test the removal schemas and publishers that don't require external dependencies."""
    print("Testing removal schemas and publishers...")
    
    try:
        # Test RemoveDocumentJob schema
        from sentra_shared.model.remove_document_job import RemoveDocumentJob
        
        job = RemoveDocumentJob(
            document_id=uuid4(),
            knowledge_source_id=uuid4(),
            user_id=uuid4()
        )
        
        # Test serialization
        job_dict = job.model_dump()
        assert all(key in job_dict for key in ['document_id', 'knowledge_source_id', 'user_id'])
        print("✓ RemoveDocumentJob schema works")
        
        # Test RemovalJobPublisher
        from sentra_shared.domain.services.removal_job_publisher import RemovalJobPublisher
        
        publisher = RemovalJobPublisher()
        assert publisher.queue == "removal_jobs"
        
        # Mock the publishing to test message formatting
        mock_channel = Mock()
        publisher.channel = mock_channel
        
        success = publisher.publish_remove_document_job(job)
        assert success is True
        
        # Verify the correct message format
        mock_channel.basic_publish.assert_called_once()
        call_args = mock_channel.basic_publish.call_args
        published_body = call_args[1]['body']
        message = json.loads(published_body)
        
        assert message['action'] == 'remove_document'
        assert 'document_id' in message
        print("✓ RemovalJobPublisher works")
        
        # Test RemovalJobConsumer
        from sentra_shared.infra.amqp.removal_job_consumer import RemovalJobConsumer
        
        consumer = RemovalJobConsumer()
        assert consumer.queue == "removal_jobs"
        print("✓ RemovalJobConsumer works")
        
        return True
        
    except Exception as e:
        print(f"✗ Removal schemas and publishers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_removal_processor_with_mocks():
    """Test the removal processor with mocked dependencies."""
    print("\nTesting removal processor with mocked dependencies...")
    
    try:
        # Mock chromadb before importing
        with patch.dict('sys.modules', {
            'chromadb': MagicMock(),
            'chromadb.config': MagicMock()
        }):
            from sentra_rag_worker.services.document_removal_processor import DocumentRemovalProcessor
            from sentra_shared.domain.enums.document import DocumentStatus
            
            # Create test data
            document_id = uuid4()
            knowledge_source_id = uuid4()
            user_id = uuid4()
            
            message = {
                "document_id": str(document_id),
                "knowledge_source_id": str(knowledge_source_id),
                "user_id": str(user_id),
                "action": "remove_document"
            }
            
            # Create processor instance
            processor = DocumentRemovalProcessor()
            
            # Mock all external dependencies
            with patch.object(processor, '_update_document_status') as mock_update_status, \
                 patch.object(processor, '_get_document') as mock_get_document, \
                 patch.object(processor, '_remove_file_from_disk') as mock_remove_file, \
                 patch.object(processor.vector_store, 'delete_document_chunks') as mock_delete_chunks:
                
                # Setup mocks
                mock_document = Mock()
                mock_document.path = "/tmp/test_document.pdf"
                mock_get_document.return_value = mock_document
                mock_update_status.return_value = True
                mock_remove_file.return_value = True
                mock_delete_chunks.return_value = 5  # 5 chunks deleted
                
                # Process the removal job
                success = processor.process_removal_job(message)
                
                # Verify the process succeeded
                assert success is True
                
                # Verify the correct sequence of calls
                assert mock_update_status.call_count == 2  # TO_BE_REMOVED and REMOVED
                mock_get_document.assert_called_once_with(document_id)
                mock_delete_chunks.assert_called_once_with(document_id)
                mock_remove_file.assert_called_once_with("/tmp/test_document.pdf")
                
                # Verify status updates
                status_calls = mock_update_status.call_args_list
                assert status_calls[0][0] == (document_id, DocumentStatus.TO_BE_REMOVED)
                assert status_calls[1][0] == (document_id, DocumentStatus.REMOVED)
                
                print("✓ Removal processor workflow works correctly")
                
            # Test error handling
            with patch.object(processor, '_update_document_status') as mock_update_status, \
                 patch.object(processor, '_get_document') as mock_get_document:
                
                # Simulate document not found
                mock_get_document.return_value = None
                mock_update_status.return_value = True
                
                success = processor.process_removal_job(message)
                assert success is False
                print("✓ Error handling works correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Removal processor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_operations():
    """Test file removal operations."""
    print("\nTesting file operations...")
    
    try:
        # Mock chromadb
        with patch.dict('sys.modules', {
            'chromadb': MagicMock(),
            'chromadb.config': MagicMock()
        }):
            from sentra_rag_worker.services.document_removal_processor import DocumentRemovalProcessor
            
            processor = DocumentRemovalProcessor()
            
            # Test file that doesn't exist (should succeed)
            non_existent_file = "/tmp/non_existent_file_12345.pdf"
            result = processor._remove_file_from_disk(non_existent_file)
            assert result is True  # Should return True for non-existent files
            print("✓ Non-existent file handling works")
            
            # Test with actual file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(b"test content")
            
            # File should exist now
            assert os.path.exists(temp_path)
            
            # Remove it
            result = processor._remove_file_from_disk(temp_path)
            assert result is True
            assert not os.path.exists(temp_path)
            print("✓ File removal works correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ File operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_worker_integration():
    """Test that the main worker can handle removal messages."""
    print("\nTesting main worker integration...")
    
    try:
        # Mock all external dependencies
        with patch.dict('sys.modules', {
            'chromadb': MagicMock(),
            'chromadb.config': MagicMock()
        }):
            from sentra_rag_worker.main import RAGWorker
            
            worker = RAGWorker()
            
            # Verify worker has removal processor
            assert hasattr(worker, 'removal_processor')
            assert hasattr(worker, 'removal_consumer')
            assert hasattr(worker, '_process_removal_message')
            
            # Test removal message processing
            message = {
                "document_id": str(uuid4()),
                "knowledge_source_id": str(uuid4()),
                "user_id": str(uuid4()),
                "action": "remove_document"
            }
            
            # Mock the processor
            with patch.object(worker.removal_processor, 'process_removal_job') as mock_process:
                mock_process.return_value = True
                
                success = worker._process_removal_message(message)
                assert success is True
                mock_process.assert_called_once_with(message)
                
                print("✓ Main worker removal message processing works")
        
        return True
        
    except Exception as e:
        print(f"✗ Main worker integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all standalone tests."""
    print("Running standalone document removal tests...")
    print("=" * 70)
    
    tests = [
        test_removal_schemas_and_publishers,
        test_removal_processor_with_mocks,
        test_file_operations,
        test_main_worker_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"Standalone tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All standalone tests passed!")
        return 0
    else:
        print("✗ Some standalone tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
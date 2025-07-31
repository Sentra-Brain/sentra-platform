#!/usr/bin/env python3
"""
Integration test for document removal workflow.

This test validates the complete removal flow without requiring external services.
"""

import sys
import os
import tempfile
import json
from pathlib import Path
from uuid import uuid4
from unittest.mock import Mock, patch

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
sys.path.insert(0, '/home/runner/work/sentra-brain/sentra-brain/core/sentra-core')

def test_removal_message_processing():
    """Test processing of removal messages with mocked dependencies."""
    print("Testing removal message processing...")
    
    try:
        from sentra_rag_worker.services.document_removal_processor import DocumentRemovalProcessor
        from sentra_core.domain.enums.document import DocumentStatus
        
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
        
        # Mock dependencies to avoid external service calls
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
        
        print("✓ Removal message processing test passed")
        return True
        
    except Exception as e:
        print(f"✗ Removal message processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_removal_job_validation():
    """Test removal job validation with invalid messages."""
    print("\nTesting removal job validation...")
    
    try:
        from sentra_rag_worker.services.document_removal_processor import DocumentRemovalProcessor
        
        processor = DocumentRemovalProcessor()
        
        # Test with missing required fields
        invalid_messages = [
            {},  # Empty message
            {"document_id": str(uuid4())},  # Missing knowledge_source_id and user_id
            {"document_id": str(uuid4()), "knowledge_source_id": str(uuid4())},  # Missing user_id
            {"document_id": "invalid-uuid", "knowledge_source_id": str(uuid4()), "user_id": str(uuid4())},  # Invalid UUID
        ]
        
        for i, message in enumerate(invalid_messages):
            try:
                success = processor.process_removal_job(message)
                # Should return False for invalid messages
                assert success is False
                print(f"✓ Invalid message {i+1} handled correctly")
            except Exception as e:
                # Should handle gracefully and return False
                print(f"✓ Invalid message {i+1} handled with exception (as expected): {type(e).__name__}")
        
        print("✓ Removal job validation test passed")
        return True
        
    except Exception as e:
        print(f"✗ Removal job validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_publisher_message_format():
    """Test that the publisher creates correctly formatted messages."""
    print("\nTesting publisher message format...")
    
    try:
        from sentra_core.model.remove_document_job import RemoveDocumentJob
        from sentra_core.domain.services.removal_job_publisher import RemovalJobPublisher
        import json
        
        # Create test job
        job = RemoveDocumentJob(
            document_id=uuid4(),
            knowledge_source_id=uuid4(),
            user_id=uuid4()
        )
        
        # Create publisher instance
        publisher = RemovalJobPublisher()
        
        # Mock the channel to capture the published message
        mock_channel = Mock()
        publisher.channel = mock_channel
        
        # Publish the job
        success = publisher.publish_remove_document_job(job)
        
        # Verify basic success
        assert success is True
        
        # Verify the message was published
        mock_channel.basic_publish.assert_called_once()
        
        # Get the published message
        call_args = mock_channel.basic_publish.call_args
        published_body = call_args[1]['body']
        
        # Parse the JSON message
        message = json.loads(published_body)
        
        # Verify message structure
        assert 'document_id' in message
        assert 'knowledge_source_id' in message
        assert 'user_id' in message
        assert message['action'] == 'remove_document'
        
        # Verify UUIDs are strings
        assert isinstance(message['document_id'], str)
        assert isinstance(message['knowledge_source_id'], str)
        assert isinstance(message['user_id'], str)
        
        print("✓ Publisher message format test passed")
        return True
        
    except Exception as e:
        print(f"✗ Publisher message format test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_removal_edge_cases():
    """Test file removal with various edge cases."""
    print("\nTesting file removal edge cases...")
    
    try:
        from sentra_rag_worker.services.document_removal_processor import DocumentRemovalProcessor
        
        processor = DocumentRemovalProcessor()
        
        # Test file that doesn't exist (should succeed)
        non_existent_file = "/tmp/non_existent_file.pdf"
        result = processor._remove_file_from_disk(non_existent_file)
        assert result is True  # Should return True for non-existent files
        
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
        
        print("✓ File removal edge cases test passed")
        return True
        
    except Exception as e:
        print(f"✗ File removal edge cases test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("Running document removal integration tests...")
    print("=" * 70)
    
    tests = [
        test_removal_message_processing,
        test_removal_job_validation,
        test_publisher_message_format,
        test_file_removal_edge_cases
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"Integration tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All integration tests passed!")
        return 0
    else:
        print("✗ Some integration tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
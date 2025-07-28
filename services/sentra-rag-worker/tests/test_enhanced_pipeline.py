#!/usr/bin/env python3
"""
Test script to verify the enhanced document processing pipeline with intermediate status updates.
"""

import sys
import os
import tempfile
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

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


def test_document_status_flow():
    """Test that document status updates correctly through the pipeline."""
    print("\nTesting document status flow...")
    
    try:
        from sentra_shared.domain.entities.document_entity import DocumentStatus
        from sentra_shared.core.logging import get_logger, set_request_id
        from sentra_rag_worker.services.document_processor import DocumentProcessor
        
        # Test that all new status values exist
        expected_statuses = ['PENDING', 'PROCESSING', 'EXTRACTING', 'CHUNKING', 'EMBEDDING', 'INDEXING', 'INDEXED', 'FAILED']
        actual_statuses = [status.name for status in DocumentStatus]
        
        for status in expected_statuses:
            assert status in actual_statuses, f"Missing status: {status}"
        
        print("✓ All required document statuses are available")
        
        # Test structured logging
        logger = get_logger("test")
        request_id = set_request_id()
        
        logger.info_step("test_step", document_id="test-doc-123", duration=1.5)
        print("✓ Structured logging works")
        
        # Test that the document processor can be instantiated
        processor = DocumentProcessor()
        print("✓ Document processor can be instantiated")
        
        return True
        
    except Exception as e:
        print(f"✗ Document status flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enhanced_logging():
    """Test enhanced logging functionality."""
    print("\nTesting enhanced logging...")
    
    try:
        from sentra_shared.core.logging import get_logger, set_request_id, get_request_id, StepTimer
        
        # Test request_id context
        original_request_id = get_request_id()
        test_request_id = set_request_id("test-request-123")
        current_request_id = get_request_id()
        
        assert current_request_id == "test-request-123", f"Request ID not set correctly: {current_request_id}"
        print("✓ Request ID context works")
        
        # Test structured logger
        logger = get_logger("test_logger")
        logger.info_step("test_operation", document_id="doc-456", duration=2.3, custom_field="test_value")
        print("✓ Structured logging works")
        
        # Test step timer
        with StepTimer(logger, "test_timing", "doc-789") as timer:
            import time
            time.sleep(0.1)  # Simulate work
        
        print("✓ Step timer works")
        
        return True
        
    except Exception as e:
        print(f"✗ Enhanced logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mock_document_processing():
    """Test document processing with mocked dependencies."""
    print("\nTesting mock document processing...")
    
    try:
        from sentra_shared.domain.entities.document_entity import DocumentStatus, DocumentFileType
        from sentra_rag_worker.services.document_processor import DocumentProcessor
        from uuid import UUID
        
        # Create a test document processor
        processor = DocumentProcessor()
        
        # Mock the dependencies
        with patch.object(processor, '_get_file_storage') as mock_file_storage, \
             patch.object(processor, 'extractor') as mock_extractor, \
             patch.object(processor, 'chunker') as mock_chunker, \
             patch.object(processor, 'embedding_service') as mock_embedding, \
             patch.object(processor, 'vector_store') as mock_vector_store, \
             patch('sentra_shared.infra.sql.postgres_service.create_db_session') as mock_db_session:
            
            # Setup mocks
            mock_file_storage.return_value.resolve_document_path.return_value = Path("/tmp/test.txt")
            mock_extractor.extract_content.return_value = "This is test content for the document."
            mock_chunker.chunk_text.return_value = ["This is test content", "for the document."]
            mock_embedding.generate_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]
            mock_vector_store.index_document_chunks.return_value = 2
            
            # Mock database and repository
            mock_db = MagicMock()
            mock_db_session.return_value = mock_db
            mock_repo = MagicMock()
            
            # Create test message
            test_message = {
                "document_id": str(uuid.uuid4()),
                "knowledge_source_id": str(uuid.uuid4()),
                "filepath": "test.txt",
                "filename": "test.txt",
                "filetype": "txt",
                "request_id": "test-request-456"
            }
            
            # Mock file validation
            with patch.object(processor, '_validate_file', return_value=True), \
                 patch.object(processor, '_update_document_status_with_repo') as mock_update_status:
                
                # Process the document
                result = processor.process_document(test_message)
                
                # Verify it succeeded
                assert result == True, "Document processing should succeed with mocked dependencies"
                
                # Verify status updates were called with expected statuses
                status_calls = [call[0][2] for call in mock_update_status.call_args_list]
                expected_status_flow = [
                    DocumentStatus.PROCESSING,
                    DocumentStatus.EXTRACTING,
                    DocumentStatus.CHUNKING,
                    DocumentStatus.EMBEDDING,
                    DocumentStatus.INDEXING,
                    DocumentStatus.INDEXED
                ]
                
                for expected_status in expected_status_flow:
                    assert expected_status in status_calls, f"Expected status {expected_status} not found in calls"
                
                print("✓ Document processing follows correct status flow")
        
        return True
        
    except Exception as e:
        print(f"✗ Mock document processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all enhanced pipeline tests."""
    print("Running enhanced document processing pipeline tests...")
    print("=" * 60)
    
    tests = [
        test_document_status_flow,
        test_enhanced_logging,
        test_mock_document_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"Enhanced pipeline tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All enhanced pipeline tests passed!")
        return 0
    else:
        print("✗ Some enhanced pipeline tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
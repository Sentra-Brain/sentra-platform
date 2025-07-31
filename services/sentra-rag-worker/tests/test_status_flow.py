#!/usr/bin/env python3
"""
Focused test script to verify the enhanced document processing status flow without heavy dependencies.
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


def test_document_status_enum():
    """Test that DocumentStatus enum has all required statuses."""
    print("\nTesting document status enum...")
    
    try:
        from sentra_core.domain.entities.document_entity import DocumentStatus
        
        # Test that all new status values exist
        expected_statuses = ['PENDING', 'PROCESSING', 'EXTRACTING', 'CHUNKING', 'EMBEDDING', 'INDEXING', 'INDEXED', 'FAILED']
        actual_statuses = [status.name for status in DocumentStatus]
        
        for status in expected_statuses:
            assert status in actual_statuses, f"Missing status: {status}"
        
        print(f"✓ All required document statuses are available: {', '.join(expected_statuses)}")
        
        # Test enum values
        assert DocumentStatus.PENDING.value == "pending"
        assert DocumentStatus.EXTRACTING.value == "extracting"
        assert DocumentStatus.CHUNKING.value == "chunking"
        assert DocumentStatus.EMBEDDING.value == "embedding"
        assert DocumentStatus.INDEXING.value == "indexing"
        assert DocumentStatus.INDEXED.value == "indexed"
        assert DocumentStatus.FAILED.value == "failed"
        
        print("✓ All status enum values are correct")
        
        return True
        
    except Exception as e:
        print(f"✗ Document status enum test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_logging():
    """Test simple logging functionality."""
    print("\nTesting simple logging...")
    
    try:
        from sentra_core.core.logging import get_logger, set_request_id, get_request_id, configure_logging
        
        # Configure logging for testing
        configure_logging(debug=True)
        
        # Test request_id context
        original_request_id = get_request_id()
        test_request_id = set_request_id("test-request-123")
        current_request_id = get_request_id()
        
        assert current_request_id == "test-request-123", f"Request ID not set correctly: {current_request_id}"
        print("✓ Request ID context works")
        
        # Test basic logger
        logger = get_logger("test_logger")
        logger.info("extracting")
        logger.info("chunking") 
        logger.info("embedding")
        logger.info("indexing")
        print("✓ Basic logging works")
        
        return True
        
    except Exception as e:
        print(f"✗ Simple logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_repository():
    """Test that the knowledge repository supports the new status_message parameter."""
    print("\nTesting knowledge repository...")
    
    try:
        from sentra_core.domain.repository.knowledge_source_repository import KnowledgeSourceRepository
        from sentra_core.domain.entities.document_entity import DocumentStatus
        from uuid import UUID
        
        # Mock database session
        mock_db = MagicMock()
        repo = KnowledgeSourceRepository(mock_db)
        
        # Mock document entity
        mock_document = MagicMock()
        mock_document.status = DocumentStatus.PENDING
        mock_document.error = None
        mock_document.status_message = None
        mock_document.chunks_count = None
        
        # Mock the get_document_by_id to return our mock document
        repo.get_document_by_id = MagicMock(return_value=mock_document)
        
        # Test updating status with message
        test_document_id = UUID('12345678-1234-5678-9012-123456789012')
        repo.update_document_status(
            test_document_id, 
            DocumentStatus.EXTRACTING, 
            error=None,
            status_message="Extracting content from document",
            chunks_count=None
        )
        
        # Verify the status was updated
        assert mock_document.status == DocumentStatus.EXTRACTING
        assert mock_document.status_message == "Extracting content from document"
        
        print("✓ Knowledge repository update_document_status supports status_message")
        
        return True
        
    except Exception as e:
        print(f"✗ Knowledge repository test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_document_entity():
    """Test that DocumentEntity has the new status_message field."""
    print("\nTesting document entity...")
    
    try:
        from sentra_core.domain.entities.document_entity import DocumentEntity, DocumentStatus
        
        # Test that DocumentEntity class is importable (basic structure test)
        # We can't instantiate it without a database, but we can check the class exists
        assert hasattr(DocumentEntity, '__tablename__')
        assert DocumentEntity.__tablename__ == "documents"
        
        print("✓ DocumentEntity class is properly defined")
        
        # Test status field and default
        status_column = None
        status_message_column = None
        
        for column in DocumentEntity.__table__.columns:
            if column.name == 'status':
                status_column = column
            elif column.name == 'status_message':
                status_message_column = column
        
        assert status_column is not None, "status column not found"
        assert status_message_column is not None, "status_message column not found"
        
        print("✓ DocumentEntity has both status and status_message fields")
        
        return True
        
    except Exception as e:
        print(f"✗ Document entity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all focused enhanced pipeline tests."""
    print("Running focused enhanced document processing pipeline tests...")
    print("=" * 70)
    
    tests = [
        test_document_status_enum,
        test_simple_logging,
        test_knowledge_repository,
        test_document_entity
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"Focused enhanced pipeline tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All focused enhanced pipeline tests passed!")
        return 0
    else:
        print("✗ Some focused enhanced pipeline tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
CLI tool to test document removal functionality by publishing removal jobs.

Usage:
  python cli_test_removal.py <document_id> <knowledge_source_id> <user_id>
"""

import sys
import os
from uuid import UUID, uuid4

# Set up environment
sys.path.insert(0, '/home/runner/work/sentra-brain/sentra-brain/core/sentra-core')

def test_publish_removal_job(document_id: str, knowledge_source_id: str, user_id: str):
    """Test publishing a removal job."""
    try:
        from sentra_core.model.remove_document_job import RemoveDocumentJob
        from sentra_core.domain.services.removal_job_publisher import RemovalJobPublisher
        
        # Create the removal job
        job = RemoveDocumentJob(
            document_id=UUID(document_id),
            knowledge_source_id=UUID(knowledge_source_id),
            user_id=UUID(user_id)
        )
        
        print(f"Created removal job: {job.model_dump()}")
        
        # Test job publishing (won't actually connect without RabbitMQ)
        publisher = RemovalJobPublisher()
        print(f"Publisher configured for queue: {publisher.queue}")
        print("Note: To actually publish, RabbitMQ server must be running")
        
        # Show what the published message would look like
        job_data = job.model_dump()
        job_data = {k: str(v) if hasattr(v, 'hex') else v for k, v in job_data.items()}
        job_data["action"] = "remove_document"
        
        print(f"Message that would be published: {job_data}")
        
        return True
        
    except Exception as e:
        print(f"Error testing removal job: {e}")
        return False

def main():
    """Main CLI function."""
    if len(sys.argv) != 4:
        print("Usage: python cli_test_removal.py <document_id> <knowledge_source_id> <user_id>")
        print("Example: python cli_test_removal.py $(python -c 'import uuid; print(uuid.uuid4())') $(python -c 'import uuid; print(uuid.uuid4())') $(python -c 'import uuid; print(uuid.uuid4())')")
        sys.exit(1)
    
    document_id = sys.argv[1]
    knowledge_source_id = sys.argv[2]
    user_id = sys.argv[3]
    
    print("Testing document removal job creation and publishing...")
    print("=" * 60)
    
    if test_publish_removal_job(document_id, knowledge_source_id, user_id):
        print("✓ Removal job test completed successfully")
        return 0
    else:
        print("✗ Removal job test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
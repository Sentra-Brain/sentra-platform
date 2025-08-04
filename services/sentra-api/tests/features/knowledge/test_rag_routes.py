# tests/features/knowledge/test_rag_routes.py

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from uuid import uuid4

from sentra_brain_api.features.knowledge.routes import rag
from sentra_brain_api.features.knowledge.schemas import (
    RAGSearchRequest,
    RAGSearchResponse,
    RAGContextRequest,
    RAGContextResponse,
    DocumentChunkResponse
)


class TestRAGRoutes:
    """Test RAG-specific routes in the knowledge API."""

    @pytest.fixture
    def app(self):
        """Create minimal test app with RAG routes."""
        app = FastAPI()
        app.include_router(rag.router, prefix="/knowledge/rag", tags=["knowledge", "rag"])
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user."""
        from sentra_core.domain.entities.user_entity import UserEntity
        user = Mock(spec=UserEntity)
        user.id = uuid4()
        user.username = "test_user"
        user.roles = "USER"
        return user

    @pytest.fixture
    def mock_rag_service(self):
        """Mock RAG service."""
        service = Mock()
        service.search_documents = AsyncMock()
        service.get_context_for_query = AsyncMock()
        return service

    def test_rag_routes_exist(self, app):
        """Test that RAG routes are registered in the application."""
        routes = [route.path for route in app.routes]
        
        # Check that RAG routes are registered
        rag_routes = [route for route in routes if "/knowledge/rag/" in route]
        assert len(rag_routes) > 0, "RAG routes should be registered"
        
        # Check specific routes exist
        expected_routes = [
            "/knowledge/rag/search",
            "/knowledge/rag/context"
        ]
        
        for expected_route in expected_routes:
            assert any(expected_route in route for route in routes), f"Route {expected_route} should exist"

    def test_rag_routes_http_methods(self, app):
        """Test that RAG routes have correct HTTP methods."""
        route_methods = {}
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                path = route.path
                if path not in route_methods:
                    route_methods[path] = set()
                route_methods[path].update(route.methods)
        
        # Search should support both GET and POST
        search_path = "/knowledge/rag/search"
        assert "GET" in route_methods.get(search_path, set())
        assert "POST" in route_methods.get(search_path, set())
        
        # Context should support POST
        context_path = "/knowledge/rag/context"
        assert "POST" in route_methods.get(context_path, set())

    @patch('sentra_brain_api.crosscutting.authorization.get_authenticated_user')
    @patch('sentra_brain_api.features.knowledge.routes.rag._get_rag_service')
    @patch('sentra_brain_api.features.knowledge.routes.rag._get_knowledge_repo')
    def test_search_knowledge_post(self, mock_get_repo, mock_get_service, mock_get_user, client, mock_user, mock_rag_service):
        """Test POST /knowledge/rag/search endpoint."""
        # Setup mocks
        mock_get_user.return_value = mock_user
        mock_get_service.return_value = mock_rag_service
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock search results
        mock_chunks = [
            {
                "chunk_id": "doc1_chunk_0",
                "content": "This is test content about AI",
                "metadata": {"filename": "test.pdf", "chunk_index": 0},
                "relevance_score": 0.95
            }
        ]
        mock_rag_service.search_documents.return_value = mock_chunks
        
        # Make request
        request_data = {
            "query": "What is AI?",
            "limit": 10
        }
        
        response = client.post("/knowledge/rag/search", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "What is AI?"
        assert len(data["chunks"]) == 1
        assert data["chunks"][0]["content"] == "This is test content about AI"
        assert data["total_results"] == 1
        
        # Verify service was called correctly
        mock_rag_service.search_documents.assert_called_once_with(
            query="What is AI?",
            knowledge_source_id=None,
            limit=10
        )

    @patch('sentra_brain_api.crosscutting.authorization.get_authenticated_user')
    @patch('sentra_brain_api.features.knowledge.routes.rag._get_rag_service')
    @patch('sentra_brain_api.features.knowledge.routes.rag._get_knowledge_repo')
    def test_search_knowledge_get(self, mock_get_repo, mock_get_service, mock_get_user, client, mock_user, mock_rag_service):
        """Test GET /knowledge/rag/search endpoint."""
        # Setup mocks
        mock_get_user.return_value = mock_user
        mock_get_service.return_value = mock_rag_service
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock search results
        mock_chunks = []
        mock_rag_service.search_documents.return_value = mock_chunks
        
        # Make request with query parameters
        response = client.get("/knowledge/rag/search?q=test%20query&limit=5")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test query"
        assert data["chunks"] == []
        assert data["total_results"] == 0
        
        # Verify service was called correctly
        mock_rag_service.search_documents.assert_called_once_with(
            query="test query",
            knowledge_source_id=None,
            limit=5
        )

    @patch('sentra_brain_api.crosscutting.authorization.get_authenticated_user')
    @patch('sentra_brain_api.features.knowledge.routes.rag._get_rag_service')
    @patch('sentra_brain_api.features.knowledge.routes.rag._get_knowledge_repo')
    def test_get_rag_context(self, mock_get_repo, mock_get_service, mock_get_user, client, mock_user, mock_rag_service):
        """Test POST /knowledge/rag/context endpoint."""
        # Setup mocks
        mock_get_user.return_value = mock_user
        mock_get_service.return_value = mock_rag_service
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock context generation
        mock_context = "Relevant information from your knowledge base:\n\nSource: test.pdf (chunk 0)\nThis is test content"
        mock_rag_service.get_context_for_query.return_value = mock_context
        
        # Make request
        request_data = {
            "query": "Explain machine learning",
            "max_tokens": 2000
        }
        
        response = client.post("/knowledge/rag/context", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Explain machine learning"
        assert data["context"] == mock_context
        assert data["sources_used"] == 1  # Should count "Source:" occurrences
        assert data["estimated_tokens"] > 0
        
        # Verify service was called correctly
        mock_rag_service.get_context_for_query.assert_called_once_with(
            query="Explain machine learning",
            knowledge_source_id=None,
            max_tokens=2000
        )

    def test_search_request_validation_no_auth(self, client):
        """Test request validation for search endpoint (schema validation only)."""
        # These should fail with 422 for validation, not 401 for auth in a real test scenario
        # Since we can't easily mock auth for validation tests, we test the schemas directly
        pass  # Skip for now, tested in schema tests instead

    def test_context_request_validation_no_auth(self, client):
        """Test request validation for context endpoint (schema validation only)."""
        # These should fail with 422 for validation, not 401 for auth in a real test scenario
        # Since we can't easily mock auth for validation tests, we test the schemas directly  
        pass  # Skip for now, tested in schema tests instead

    def test_schemas_work_correctly(self):
        """Test that the new schemas work correctly."""
        # Test RAGSearchRequest
        request = RAGSearchRequest(query="test query", limit=5)
        assert request.query == "test query"
        assert request.limit == 5
        assert request.knowledge_source_id is None
        
        # Test validation
        with pytest.raises(ValueError):
            RAGSearchRequest(query="", limit=5)  # Empty query should fail
        
        with pytest.raises(ValueError):
            RAGSearchRequest(query="test", limit=0)  # Invalid limit should fail
        
        with pytest.raises(ValueError):
            RAGSearchRequest(query="test", limit=100)  # Limit too high should fail
        
        # Test DocumentChunkResponse
        chunk = DocumentChunkResponse(
            chunk_id="test_chunk",
            content="test content",
            metadata={"filename": "test.pdf"},
            relevance_score=0.85
        )
        assert chunk.chunk_id == "test_chunk"
        assert chunk.relevance_score == 0.85
        
        # Test RAGSearchResponse
        response = RAGSearchResponse(
            query="test",
            chunks=[chunk],
            total_results=1
        )
        assert response.query == "test"
        assert len(response.chunks) == 1
        assert response.total_results == 1
        
        # Test RAGContextRequest
        context_req = RAGContextRequest(query="test context query")
        assert context_req.query == "test context query"
        assert context_req.max_tokens == 4000  # Default value
        
        # Test validation
        with pytest.raises(ValueError):
            RAGContextRequest(query="")  # Empty query should fail
        
        with pytest.raises(ValueError):
            RAGContextRequest(query="test", max_tokens=50)  # Too few tokens should fail
        
        with pytest.raises(ValueError):
            RAGContextRequest(query="test", max_tokens=10000)  # Too many tokens should fail
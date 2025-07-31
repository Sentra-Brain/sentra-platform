# tests/features/knowledge/test_restful_routes.py

import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from sentra_brain_api.features.knowledge.routes import sources, documents


class TestRESTfulRoutes:
    @pytest.fixture
    def app(self):
        """Create a test FastAPI app with the new RESTful routes"""
        app = FastAPI()
        app.include_router(sources.router, prefix="/knowledge/sources", tags=["knowledge"])
        app.include_router(documents.router, prefix="/knowledge", tags=["knowledge"])
        return app

    def test_sources_routes_created(self, app):
        """Test that the sources routes are created correctly"""
        routes = [route.path for route in app.routes]
        
        # Check sources routes
        assert "/knowledge/sources" in routes
        assert "/knowledge/sources/{knowledge_source_id}" in routes
        
    def test_documents_routes_created(self, app):
        """Test that the documents routes are created correctly"""
        routes = [route.path for route in app.routes]
        
        # Check nested document routes
        assert "/knowledge/sources/{knowledge_source_id}/documents" in routes
        
        # Check root-level document routes
        assert "/knowledge/documents" in routes
        assert "/knowledge/documents/{document_id}" in routes

    def test_sources_http_methods(self, app):
        """Test that sources routes have correct HTTP methods"""
        route_methods = {}
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                path = route.path
                if path not in route_methods:
                    route_methods[path] = set()
                route_methods[path].update(route.methods)
        
        # Sources should support GET and POST
        sources_path = "/knowledge/sources"
        assert "GET" in route_methods.get(sources_path, set())
        assert "POST" in route_methods.get(sources_path, set())
        
        # Individual source should support GET, PATCH, DELETE
        source_detail_path = "/knowledge/sources/{knowledge_source_id}"
        assert "GET" in route_methods.get(source_detail_path, set())
        assert "PATCH" in route_methods.get(source_detail_path, set())
        assert "DELETE" in route_methods.get(source_detail_path, set())

    def test_documents_http_methods(self, app):
        """Test that documents routes have correct HTTP methods"""
        route_methods = {}
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                path = route.path
                if path not in route_methods:
                    route_methods[path] = set()
                route_methods[path].update(route.methods)
        
        # Nested documents should support GET and POST
        nested_docs_path = "/knowledge/sources/{knowledge_source_id}/documents"
        assert "GET" in route_methods.get(nested_docs_path, set())
        assert "POST" in route_methods.get(nested_docs_path, set())
        
        # Root documents should support GET
        docs_list_path = "/knowledge/documents"
        assert "GET" in route_methods.get(docs_list_path, set())
        
        # Individual document should support GET, PATCH, DELETE
        doc_detail_path = "/knowledge/documents/{document_id}"
        assert "GET" in route_methods.get(doc_detail_path, set())
        assert "PATCH" in route_methods.get(doc_detail_path, set())
        assert "DELETE" in route_methods.get(doc_detail_path, set())

    def test_restful_structure_compliance(self, app):
        """Test that the route structure follows RESTful conventions"""
        routes = [route.path for route in app.routes]
        
        # Should have collection and item routes for sources
        assert "/knowledge/sources" in routes  # Collection
        assert "/knowledge/sources/{knowledge_source_id}" in routes  # Item
        
        # Should have nested collection for documents under sources
        assert "/knowledge/sources/{knowledge_source_id}/documents" in routes
        
        # Should have separate root-level document operations
        assert "/knowledge/documents" in routes  # Collection
        assert "/knowledge/documents/{document_id}" in routes  # Item
        
        # Should NOT have the old non-RESTful routes
        assert "/knowledge/upload" not in routes
        assert "/knowledge/knowledge-sources/{knowledge_source_id}/status" not in routes
# Test: Compare old vs new route implementation to ensure functionality is preserved

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import Mock

from sentra_brain_api.features.knowledge.controller import KnowledgeController
from sentra_brain_api.features.knowledge.routes import sources, documents


class TestBackwardCompatibilityAndFunctionality:
    """Test that the new RESTful structure provides all the functionality of the old controller"""
    
    def test_old_controller_still_works(self):
        """Verify the old controller still functions (for comparison)"""
        app = FastAPI()
        controller = KnowledgeController()
        app.include_router(controller.router, prefix="/knowledge", tags=["knowledge"])
        
        # Should have the old routes
        routes = [route.path for route in app.routes]
        assert "/knowledge/upload" in routes
        assert "/knowledge/knowledge-sources" in routes
    
    def test_new_restful_routes_functional_equivalent(self):
        """Test that new routes provide same core functionality as old ones"""
        app = FastAPI()
        app.include_router(sources.router, prefix="/knowledge/sources", tags=["knowledge"])
        app.include_router(documents.router, prefix="/knowledge", tags=["knowledge"])
        
        routes = {route.path: route for route in app.routes if hasattr(route, 'path')}
        
        # Core functionality mapping
        functionality_mapping = {
            # Old -> New functionality
            "list_sources": "/knowledge/sources",  # GET
            "create_source": "/knowledge/sources",  # POST  
            "get_single_source": "/knowledge/sources/{knowledge_source_id}",  # GET (new)
            "update_source_status": "/knowledge/sources/{knowledge_source_id}",  # PATCH
            "delete_source": "/knowledge/sources/{knowledge_source_id}",  # DELETE (new)
            "upload_document": "/knowledge/sources/{knowledge_source_id}/documents",  # POST
            "list_documents_in_source": "/knowledge/sources/{knowledge_source_id}/documents",  # GET
            "list_all_documents": "/knowledge/documents",  # GET
            "get_document": "/knowledge/documents/{document_id}",  # GET (new)
            "update_document": "/knowledge/documents/{document_id}",  # PATCH (new)
            "delete_document": "/knowledge/documents/{document_id}",  # DELETE
        }
        
        # Verify all functionality is covered
        for functionality, expected_route in functionality_mapping.items():
            assert expected_route in routes, f"Missing route for {functionality}: {expected_route}"
    
    def test_enhanced_functionality(self):
        """Test that new structure provides enhanced functionality not available in old API"""
        app = FastAPI()
        app.include_router(sources.router, prefix="/knowledge/sources", tags=["knowledge"])
        app.include_router(documents.router, prefix="/knowledge", tags=["knowledge"])
        
        routes = [route.path for route in app.routes]
        
        # New functionality not available in old API
        new_features = [
            "/knowledge/sources/{knowledge_source_id}",  # GET single source
            "/knowledge/sources/{knowledge_source_id}",  # DELETE source
            "/knowledge/documents/{document_id}",  # GET single document
            "/knowledge/documents/{document_id}",  # PATCH document metadata
        ]
        
        for feature in new_features:
            assert feature in routes, f"New feature not implemented: {feature}"
    
    def test_restful_principles_compliance(self):
        """Verify the new API follows RESTful principles"""
        app = FastAPI()
        app.include_router(sources.router, prefix="/knowledge/sources", tags=["knowledge"])
        app.include_router(documents.router, prefix="/knowledge", tags=["knowledge"])
        
        route_methods = {}
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                path = route.path
                if path not in route_methods:
                    route_methods[path] = set()
                route_methods[path].update(route.methods)
        
        # RESTful principles check
        restful_patterns = {
            # Collection endpoints
            "/knowledge/sources": ["GET", "POST"],  # List & Create
            "/knowledge/documents": ["GET"],  # List 
            "/knowledge/sources/{knowledge_source_id}/documents": ["GET", "POST"],  # List & Create nested
            
            # Item endpoints  
            "/knowledge/sources/{knowledge_source_id}": ["GET", "PATCH", "DELETE"],  # CRUD operations
            "/knowledge/documents/{document_id}": ["GET", "PATCH", "DELETE"],  # CRUD operations
        }
        
        for path, expected_methods in restful_patterns.items():
            actual_methods = route_methods.get(path, set())
            for method in expected_methods:
                assert method in actual_methods, f"Missing {method} method for {path}"
    
    def test_no_legacy_non_restful_routes(self):
        """Ensure old non-RESTful routes are not present in new structure"""
        app = FastAPI()
        app.include_router(sources.router, prefix="/knowledge/sources", tags=["knowledge"])
        app.include_router(documents.router, prefix="/knowledge", tags=["knowledge"])
        
        routes = [route.path for route in app.routes]
        
        # These should NOT exist in the new RESTful API
        legacy_routes = [
            "/knowledge/upload",  # Replaced by POST /sources/{id}/documents
            "/knowledge/knowledge-sources/{knowledge_source_id}/status",  # Replaced by PATCH /sources/{id}
        ]
        
        for legacy_route in legacy_routes:
            # Check if any route matches the legacy pattern (accounting for prefix differences)
            legacy_found = any(
                legacy_route.replace("/knowledge/", "") in route.replace("/knowledge/", "") 
                for route in routes
            )
            assert not legacy_found, f"Legacy non-RESTful route still present: {legacy_route}"
# tests/features/knowledge/test_knowledge_controller.py

import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from sentra_brain_api.features.knowledge.controller import KnowledgeController


class TestKnowledgeController:
    @pytest.fixture
    def controller(self):
        return KnowledgeController()

    def test_controller_creates_routes(self, controller):
        """Test that the controller creates the expected routes"""
        assert controller.router is not None
        
        # Check that routes are registered
        routes = [route.path for route in controller.router.routes]
        expected_routes = [
            "/upload",
            "/knowledge-sources",
            "/documents"
        ]
        
        for expected_route in expected_routes:
            assert expected_route in routes, f"Route {expected_route} not found in {routes}"

    def test_controller_has_correct_methods(self, controller):
        """Test that the controller has the expected HTTP methods"""
        route_methods = {}
        for route in controller.router.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                path = route.path
                if path not in route_methods:
                    route_methods[path] = set()
                route_methods[path].update(route.methods)
        
        # Check specific method requirements
        assert "POST" in route_methods.get("/upload", set())
        assert "POST" in route_methods.get("/knowledge-sources", set())
        assert "GET" in route_methods.get("/knowledge-sources", set())
        assert "GET" in route_methods.get("/documents", set())

    def test_route_integration_in_app(self):
        """Test that routes can be integrated into a FastAPI app"""
        app = FastAPI()
        controller = KnowledgeController()
        
        # This should not raise an exception
        app.include_router(controller.router, prefix="/knowledge", tags=["knowledge"])
        
        # Verify routes are accessible via the app
        routes = [route.path for route in app.routes]
        assert any("/knowledge" in route for route in routes)
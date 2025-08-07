import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sentra_core.domain.entities.organization_entity import OrganizationEntity
from sentra_brain_api.main import create_app
from sentra_core.infra.sql.postgres_service import get_db


class TestOrganizationController:
    
    @pytest.fixture
    def mock_organization(self):
        return OrganizationEntity(
            name="Test Organization",
            slug="test-org",
            description="A test organization",
            location="Test City",
            contact_email="test@example.com"
        )
    
    @pytest.fixture
    def client(self):
        app = create_app()
        
        # Override database dependency
        def get_db_override():
            return MagicMock()
        
        app.dependency_overrides[get_db] = get_db_override
        
        with TestClient(app) as client:
            yield client
    
    def test_get_organization_not_found(self, client):
        """Test GET /organization when no organization exists"""
        with client as test_client:
            # Mock the database query to return None
            response = test_client.get("/organization")
            # Should return 404 when no organization exists
            assert response.status_code == 404
            assert "No organization found" in response.json()["detail"]
    
    def test_patch_organization_not_found(self, client):
        """Test PATCH /organization when no organization exists"""
        with client as test_client:
            response = test_client.patch("/organization", json={
                "name": "Updated Organization"
            })
            # Should return 404 when no organization exists
            assert response.status_code == 404
            assert "No organization found" in response.json()["detail"]
import pytest
from unittest.mock import MagicMock, patch
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
    
    @patch('sentra_brain_api.features.organization.api_service.OrganizationService')
    def test_get_organization_not_found(self, mock_org_service_class, client):
        """Test GET /organization when no organization exists"""
        # Mock the service to return None for get_current_org
        mock_service_instance = MagicMock()
        mock_service_instance.get_current_org.return_value = None
        mock_org_service_class.return_value = mock_service_instance
        
        with client as test_client:
            response = test_client.get("/organization")
            # Should return 404 when no organization exists
            assert response.status_code == 404
            assert "No organization found" in response.json()["detail"]
    
    @patch('sentra_brain_api.features.organization.api_service.OrganizationService')
    def test_patch_organization_not_found(self, mock_org_service_class, client):
        """Test PATCH /organization when no organization exists"""
        # Mock the service to raise ValueError for update_current_org when no org exists
        mock_service_instance = MagicMock()
        mock_service_instance.update_current_org.side_effect = ValueError("No organization found")
        mock_org_service_class.return_value = mock_service_instance
        
        with client as test_client:
            response = test_client.patch("/organization", json={
                "name": "Updated Organization"
            })
            # Should return 404 when no organization exists
            assert response.status_code == 404
            assert "No organization found" in response.json()["detail"]
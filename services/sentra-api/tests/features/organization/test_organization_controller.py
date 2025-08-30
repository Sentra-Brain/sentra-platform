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
        from sentra_brain_api.core.lifecycle_config import AppLifecycleConfig

        app = create_app(AppLifecycleConfig(init_mcp=False, init_db=False))

        # Override database dependency
        def get_db_override():
            return MagicMock()

        app.dependency_overrides[get_db] = get_db_override

        return TestClient(app)
    
    @patch('sentra_brain_api.features.organization.api_service.OrganizationService')
    def test_get_organization_not_found(self, mock_org_service_class, client):
        mock_service_instance = MagicMock()
        mock_service_instance.get_current_org.return_value = None
        mock_org_service_class.return_value = mock_service_instance

        response = client.get("/organization")
        assert response.status_code == 404
        assert "No organization found" in response.json()["detail"]

    @patch('sentra_brain_api.features.organization.api_service.OrganizationService')
    def test_patch_organization_not_found(self, mock_org_service_class, client):
        mock_service_instance = MagicMock()
        mock_service_instance.update_current_org.side_effect = ValueError("No organization found")
        mock_org_service_class.return_value = mock_service_instance

        response = client.patch("/organization", json={
            "name": "Updated Organization"
        })
        assert response.status_code == 404
        assert "No organization found" in response.json()["detail"]

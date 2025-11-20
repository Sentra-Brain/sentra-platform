# sentra_brain_api/features/public/api_service.py

from sqlalchemy.orm import Session
from sentra_brain_api.features.public.schemas import PublicSettingsResponse
from sentra.domain.services.system_settings_service import SystemSettingsService

class PublicApiService:
    def __init__(self, db: Session):
        self.system_settings_service = SystemSettingsService(db)

    def get_public_settings(self) -> PublicSettingsResponse:
        workspace_name, max_users, available = self.system_settings_service.get_public_settings()
        return PublicSettingsResponse.model_validate({
            "workspace_name": workspace_name,
            "max_users": max_users,
            "available_slots": available
        })
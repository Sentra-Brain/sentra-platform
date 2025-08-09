# sentra_brain_api/features/settings/api_service.py

from sqlalchemy.orm import Session
from sentra_core.domain.services.settings_service import SettingsService
from sentra_brain_api.features.settings.schemas import (
    SystemSettingsResponse,
    SystemSettingsUpdateRequest,
    ChatSettingsResponse,
    ChatSettingsUpdateRequest
)
from sentra_brain_api.features.settings.mappers import (
    to_system_settings_response,
    to_chat_settings_response
)


class SettingsApiService:
    def __init__(self, db: Session):
        self.service = SettingsService(db)

    def get_system_settings(self) -> SystemSettingsResponse:
        settings = self.service.get_system_settings()
        return to_system_settings_response(settings)

    def update_system_settings(self, request: SystemSettingsUpdateRequest) -> SystemSettingsResponse:
        # Convert to dict excluding unset values
        update_data = request.model_dump(exclude_unset=True)
        settings = self.service.update_system_settings(update_data)
        return to_system_settings_response(settings)

    def get_chat_settings(self) -> ChatSettingsResponse:
        settings = self.service.get_chat_settings()
        return to_chat_settings_response(settings)

    def update_chat_settings(self, request: ChatSettingsUpdateRequest) -> ChatSettingsResponse:
        # Convert to dict excluding unset values
        update_data = request.model_dump(exclude_unset=True)
        settings = self.service.update_chat_settings(update_data)
        return to_chat_settings_response(settings)
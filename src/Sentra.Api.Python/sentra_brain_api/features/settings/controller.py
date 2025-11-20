# sentra_brain_api/features/settings/controller.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sentra_brain_api.crosscutting.authorization import get_superadmin_user
from sentra_brain_api.features.settings.api_service import SettingsApiService
from sentra_brain_api.features.settings.schemas import (
    SystemSettingsResponse,
    SystemSettingsUpdateRequest,
    ChatSettingsResponse,
    ChatSettingsUpdateRequest
)
from sentra.infra.sql.postgres_service import get_db


class SettingsController:
    def __init__(self):
        self.router = APIRouter(dependencies=[Depends(get_superadmin_user)])
        self._add_routes()

    def _add_routes(self):
        @self.router.get("/settings/system", response_model=SystemSettingsResponse)
        def get_system_settings(db: Session = Depends(get_db)):
            service = SettingsApiService(db)
            return service.get_system_settings()

        @self.router.patch("/settings/system", response_model=SystemSettingsResponse)
        def update_system_settings(
            request: SystemSettingsUpdateRequest,
            db: Session = Depends(get_db)
        ):
            service = SettingsApiService(db)
            return service.update_system_settings(request)

        @self.router.get("/settings/chat", response_model=ChatSettingsResponse)
        def get_chat_settings(db: Session = Depends(get_db)):
            service = SettingsApiService(db)
            return service.get_chat_settings()

        @self.router.patch("/settings/chat", response_model=ChatSettingsResponse)
        def update_chat_settings(
            request: ChatSettingsUpdateRequest,
            db: Session = Depends(get_db)
        ):
            service = SettingsApiService(db)
            return service.update_chat_settings(request)
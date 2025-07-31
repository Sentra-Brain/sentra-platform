# sentra_brain_api/features/public/controller.py
from fastapi import APIRouter, Depends
from sentra_brain_api.features.public.api_service import PublicApiService
from sentra_core.infra.sql.postgres_service import get_db
from sqlalchemy.orm import Session
from sentra_brain_api.features.public.schemas import PublicSettingsResponse
from sentra_brain_api.features.public.constants import PUBLIC_SETTINGS_DESCRIPTION

class PublicSettingsController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.get("/settings", response_model=PublicSettingsResponse, description=PUBLIC_SETTINGS_DESCRIPTION, tags=["public"])
        def get_public_settings(db: Session = Depends(get_db)):
            return PublicApiService(db).get_public_settings()

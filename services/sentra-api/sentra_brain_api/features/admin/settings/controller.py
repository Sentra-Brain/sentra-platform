# sentra_brain_api/features/admin/settings/settings_controller.py
from fastapi import APIRouter, Depends
from sentra_brain_api.crosscutting.authorization import get_superadmin_user
from sentra_brain_api.features.admin.settings.mappers import to_system_settings_response
from sentra_core.domain.entities.system_settings import SystemSettingsEntity
from sentra_brain_api.features.admin.settings.schemas import SystemSettingsResponse
from sentra_core.infra.sql.postgres_service import get_db
from sqlalchemy.orm import Session


class SettingsController:
    def __init__(self):
        self.router = APIRouter(dependencies=[Depends(get_superadmin_user)])
        self._add_routes()

    def _add_routes(self):
        @self.router.get("/settings", response_model=SystemSettingsResponse)
        def get_settings(db: Session = Depends(get_db)):
            settings = db.query(SystemSettingsEntity).first()
            return to_system_settings_response(settings)

        @self.router.put("/settings", response_model=SystemSettingsResponse)
        def update_settings(data: SystemSettingsResponse, db: Session = Depends(get_db)):
            settings = db.query(SystemSettingsEntity).first()
            settings.max_users = data.max_users
            db.commit()
            db.refresh(settings)
            return to_system_settings_response(settings)

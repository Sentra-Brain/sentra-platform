# sentra_brain_api/features/admin/settings/settings_controller.py
from fastapi import APIRouter, Depends
from sentra_brain_api.crosscutting.authorization import get_superadmin_user
from sentra_shared.domain.entities.system_settings import SystemSettings
from sentra_brain_api.features.admin.settings.models import SystemSettingsModel
from sentra_shared.infra.sql.postgres_service import get_db
from sqlalchemy.orm import Session


class SettingsController:
    def __init__(self):
        self.router = APIRouter(dependencies=[Depends(get_superadmin_user)])
        self._add_routes()

    def _add_routes(self):
        @self.router.get("/settings", response_model=SystemSettingsModel)
        def get_settings(db: Session = Depends(get_db)):
            settings = db.query(SystemSettings).first()
            return SystemSettingsModel.model_validate(settings, from_attributes=True)

        @self.router.put("/settings", response_model=SystemSettingsModel)
        def update_settings(data: SystemSettingsModel, db: Session = Depends(get_db)):
            settings = db.query(SystemSettings).first()
            settings.max_users = data.max_users
            db.commit()
            db.refresh(settings)
            return SystemSettingsModel.model_validate(settings, from_attributes=True)

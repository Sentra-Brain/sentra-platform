# sentra_brain_api/features/public/public_controller.py
from fastapi import APIRouter, Depends
from sentra_brain_api.domain.system_settings import SystemSettings
from sentra_brain_api.domain.user import UserEntity
from sentra_brain_api.features.public.models import PublicSettingsModel
from sentra_brain_api.infra.postgres_service import get_db
from sqlalchemy.orm import Session

class PublicSettingsController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.get("/settings", response_model=PublicSettingsModel, tags=["public"])
        def get_public_settings(db: Session = Depends(get_db)):
            settings = db.query(SystemSettings).first()
            total_users = db.query(UserEntity).filter(~UserEntity.username.in_(["superadmin", "admin"])).count()

            if settings.max_users == -1:
                available = -1  # indicates "unlimited"
            else:
                available = max(0, settings.max_users - total_users)

            return PublicSettingsModel(
                workspace_name=settings.workspace_name,
                max_users=settings.max_users,
                available_slots=available
            )


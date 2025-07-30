# sentra_shared/domain/system_settings.py

from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sentra_shared.domain.entities.base_entity import BaseEntity


class SystemSettingsEntity(BaseEntity):
    __tablename__ = "system_settings"

    workspace_name: Mapped[str] = mapped_column(String(255), default="Sentra Brain")
    license_type: Mapped[str] = mapped_column(String(32), default="community")
    maintenance_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    default_language: Mapped[str] = mapped_column(String(8), default="en")
    log_retention_days: Mapped[int] = mapped_column(Integer, default=30)
    max_users: Mapped[int] = mapped_column(Integer, default=3)

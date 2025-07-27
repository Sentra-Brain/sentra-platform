# sentra_brain_api/domain/system_settings.py
from sqlalchemy import Column, Integer, String, Boolean
from sentra_shared.domain.entities.base_entity import BaseEntity

class SystemSettings(BaseEntity):
    __tablename__ = "system_settings"

    workspace_name = Column(String(255), default="Sentra Brain")
    license_type = Column(String(32), default="community")
    maintenance_mode = Column(Boolean, default=False)
    default_language = Column(String(8), default="en")
    log_retention_days = Column(Integer, default=30)
    max_users = Column(Integer, default=3)

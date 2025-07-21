# domain/system_settings.py

from sqlalchemy import Column, Integer, String, Boolean, JSON
from sentra_brain_api.domain.base_entity import BaseEntity

class SystemSettings(BaseEntity):
    """
    Represents global configuration for the Sentra Brain instance.
    These settings affect system-wide behavior and limits.
    """

    __tablename__ = "system_settings"

    # Primary key (only one row expected in practice)
    id = Column(Integer, primary_key=True)

    # Workspace name shown in the Admin UI and logs
    workspace_name = Column(String(255), default="Sentra Brain")

    # Deployment type: "community", "enterprise", "custom"
    license_type = Column(String(32), default="community")

    # Enables/disables maintenance mode (locks users out except admin)
    maintenance_mode = Column(Boolean, default=False)

    # UI language or localization default (e.g., "en", "es")
    default_language = Column(String(8), default="en")

    # Retention period for logs in days
    log_retention_days = Column(Integer, default=30)
    
    # Maximum number of allowed users (3 for Community edition)
    max_users = Column(Integer, default=3)

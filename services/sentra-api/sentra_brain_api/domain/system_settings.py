# domain/system_settings.py
from sqlalchemy import Column, Integer
from sentra_brain_api.domain.base_entity import BaseEntity

class SystemSettings(BaseEntity):
    __tablename__ = "system_settings"
    id = Column(Integer, primary_key=True)
    max_users = Column(Integer, default=3)

# services/sentra-shared/sentra_shared/domain/base_entity.py

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr, DeclarativeBase

class Base(DeclarativeBase):
    pass

class BaseEntity(Base):
    __abstract__ = True

    @declared_attr
    def id(cls):
        return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, onupdate=datetime.now(timezone.utc), nullable=True)

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sentra.domain.entities.base_entity import BaseEntity


class OrganizationEntity(BaseEntity):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    contact_email: Mapped[str] = mapped_column(String, nullable=True)
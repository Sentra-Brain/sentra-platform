from sqlalchemy.orm import Session
from sentra.domain.entities.organization_entity import OrganizationEntity
from sentra.domain.repository.base_repository import BaseRepository


class OrganizationRepository(BaseRepository[OrganizationEntity]):
    def __init__(self, db: Session):
        super().__init__(OrganizationEntity, db)
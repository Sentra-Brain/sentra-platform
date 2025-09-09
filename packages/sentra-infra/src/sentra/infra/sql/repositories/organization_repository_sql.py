# packages/sentra-infra/src/sentra/infra/sql/repositories/organization_repository_sql.py
from sqlalchemy.orm import Session
from sentra.domain.entities.organization_entity import OrganizationEntity
from sentra.domain.repository.organization_repository import IOrganizationRepository
from sentra.infra.sql.repositories.base_repository import BaseRepository

class OrganizationRepositorySql(BaseRepository[OrganizationEntity], IOrganizationRepository):
    def __init__(self, db: Session):
        super().__init__(OrganizationEntity, db)

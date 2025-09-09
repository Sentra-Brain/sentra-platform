from sqlalchemy.orm import Session
from sentra.domain.entities.organization_entity import OrganizationEntity
from sentra.domain.repository.organization_repository import IOrganizationRepository


class OrganizationService:
    def __init__(self, repo: IOrganizationRepository):
        self.repo = repo

    def get_current_org(self) -> OrganizationEntity:
        return self.repo.db.query(OrganizationEntity).first()

    def update_current_org(self, update_data: dict) -> OrganizationEntity:
        org = self.get_current_org()
        if not org:
            raise ValueError("No organization found. Please create an organization first.")
        for field, value in update_data.items():
            setattr(org, field, value)
        self.repo.update(org)
        return org

    def create_organization(self, org_data: dict) -> OrganizationEntity:
        """Create a new organization. Used for initial setup."""
        org = OrganizationEntity(**org_data)
        return self.repo.create(org)
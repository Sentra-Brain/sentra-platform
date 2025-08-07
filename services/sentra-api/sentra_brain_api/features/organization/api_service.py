from sqlalchemy.orm import Session
from sentra_core.domain.services.organization_service import OrganizationService


class OrganizationApiService:
    def __init__(self, db: Session):
        self.service = OrganizationService(db)

    def get(self):
        return self.service.get_current_org()

    def update(self, update):
        return self.service.update_current_org(update.model_dump(exclude_unset=True))
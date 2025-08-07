from sqlalchemy.orm import Session
from fastapi import HTTPException
from sentra_core.domain.services.organization_service import OrganizationService


class OrganizationApiService:
    def __init__(self, db: Session):
        self.service = OrganizationService(db)

    def get(self):
        org = self.service.get_current_org()
        if not org:
            raise HTTPException(status_code=404, detail="No organization found")
        return org

    def update(self, update):
        try:
            return self.service.update_current_org(update.model_dump(exclude_unset=True))
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
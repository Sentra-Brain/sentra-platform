from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sentra_core.infra.sql.postgres_service import get_db
from sentra_brain_api.features.organization.api_service import OrganizationApiService
from sentra_brain_api.features.organization.schemas import OrganizationResponse, OrganizationUpdateRequest
from sentra_brain_api.features.organization.mappers import to_organization_model

router = APIRouter()


@router.get("/organization", response_model=OrganizationResponse)
def get_organization(db: Session = Depends(get_db)):
    return to_organization_model(OrganizationApiService(db).get())


@router.patch("/organization", response_model=OrganizationResponse)
def update_organization(update: OrganizationUpdateRequest, db: Session = Depends(get_db)):
    return to_organization_model(OrganizationApiService(db).update(update))
from sentra.domain.entities.organization_entity import OrganizationEntity
from sentra_brain_api.features.organization.schemas import OrganizationResponse


def to_organization_model(org: OrganizationEntity) -> OrganizationResponse:
    return OrganizationResponse(
        name=org.name,
        slug=org.slug,
        description=org.description,
        location=org.location,
        contact_email=org.contact_email
    )
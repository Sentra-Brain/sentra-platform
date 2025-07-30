from sentra_brain_api.features.admin.settings.schemas import SystemSettingsResponse
from sentra_shared.domain.entities.system_settings import SystemSettingsEntity

def to_system_settings_response(settings: SystemSettingsEntity) -> SystemSettingsResponse:
    return SystemSettingsResponse(
        id=settings.id,
        workspace_name=settings.workspace_name,
        license_type=settings.license_type,
        maintenance_mode=settings.maintenance_mode,
        default_language=settings.default_language,
        log_retention_days=settings.log_retention_days,
        max_users=settings.max_users
    )

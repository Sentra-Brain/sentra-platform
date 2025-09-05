from sentra_brain_api.features.admin.settings.schemas import SystemSettingsResponse
from sentra.domain.entities.system_settings import SystemSettingsEntity

def to_system_settings_response(settings: SystemSettingsEntity) -> SystemSettingsResponse:
    return SystemSettingsResponse(
        id=str(settings.id),
        workspace_name=settings.workspace_name,
        license_type=settings.license_type,
        maintenance_mode=settings.maintenance_mode,
        default_language=settings.default_language,
        log_retention_days=settings.log_retention_days,
        max_users=settings.max_users,
        enable_web_search=settings.enable_web_search,
        web_search_region=settings.web_search_region,
        max_web_results=settings.max_web_results,
        cache_results=settings.cache_results,
        cache_expiration_hours=settings.cache_expiration_hours,
        context_limit_chars=settings.context_limit_chars,
        default_timezone=settings.default_timezone
    )

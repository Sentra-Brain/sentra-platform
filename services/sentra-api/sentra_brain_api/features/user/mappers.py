# sentra_brain_api/features/user/mappers.py

from sentra_core.domain.entities.user_entity import UserEntity
from sentra_brain_api.features.user.schemas import UserModel, UserProfileResponse

def to_user_model(user: UserEntity) -> UserModel:
    return UserModel(
        id=str(user.id) if user.id else None,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled,
        roles=user.get_roles() if hasattr(user, "get_roles") else [],
    )


def to_user_profile_response(user: UserEntity) -> UserProfileResponse:
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        job_title=getattr(user, 'job_title', None),
        avatar_url=getattr(user, 'avatar_url', None),
        phone_number=getattr(user, 'phone_number', None),
        bio=getattr(user, 'bio', None),
        preferred_language=getattr(user, 'preferred_language', 'es'),
        timezone=getattr(user, 'timezone', 'Europe/Madrid'),
        roles=[role.value for role in user.get_roles()] if hasattr(user, "get_roles") else [],
    )

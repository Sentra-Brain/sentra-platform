# sentra_brain_api/features/user/mappers.py

from sentra_core.domain.entities.user_entity import UserEntity
from sentra_brain_api.features.user.schemas import UserModel

def to_user_model(user: UserEntity) -> UserModel:
    return UserModel(
        id=str(user.id) if user.id else None,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled,
        roles=user.get_roles() if hasattr(user, "get_roles") else [],
    )

"""API для ролей"""

from fastapi import APIRouter, Security, status

from app import services
from app.dependencies import anauthorized_exception, get_current_user
from app.models.user import User

router = APIRouter(tags=["role"])


@router.post("/role", status_code=status.HTTP_201_CREATED)
async def create_role(
    role: str,
    description: str,
    current_user: User = Security(get_current_user, scopes=["administrator"]),
) -> None:
    """Создание новой роли"""

    if not current_user:
        raise anauthorized_exception

    await services.role.create(role, description)

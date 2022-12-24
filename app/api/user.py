"""API для пользователя"""

from fastapi import APIRouter, Depends, status

from app import services
from app.dependencies import get_current_user
from app.models.responses import UserResponse
from app.models.user import User, UserRegistration

router = APIRouter(tags=["user"])


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_yourself(
    current_user: User = Depends(get_current_user),
) -> User:
    """Получить себя"""

    return await services.user.get_repr(current_user.username)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_users() -> list[User]:
    """Получить всех пользователей"""

    return await services.user.get_list()


@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
async def register_a_new_user(
    user: UserRegistration,
) -> UserResponse:
    """Регистрация нового пользователя"""

    return await services.user.create(user)


@router.get("/{username}", status_code=status.HTTP_200_OK)
async def get_user_by_username(username: str) -> User:
    """Получить конкретного пользователя по имени"""

    return await services.user.get_repr(username)


@router.get("/{id}", status_code=status.HTTP_200_OK, deprecated=True)
async def get_user_by_id(id: int) -> User:
    """Получить конкретного пользователя по айди"""

    return await services.user.get_repr_by_id(id)

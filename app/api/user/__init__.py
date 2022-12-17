"""API для пользователя"""
from asyncpg import Record
from fastapi import APIRouter, Depends

from app.api.user import admin, auth
from app.dependencies import anauthorized_exception, get_current_user
from app.models.user import User
from app.services.user import get_list, get_repr

router = APIRouter(tags=["user"])
router.include_router(auth.router)
router.include_router(admin.router)


@router.get("/user/{username}")
async def user(username: str, current_user: User | None = Depends(get_current_user)) -> User:
    """Получить конкретного пользователя"""

    if not current_user:
        raise anauthorized_exception

    return await get_repr(username)


@router.get("/user")
async def get_users(
    current_user: User | None = Depends(get_current_user),
) -> list[Record]:
    """Получить всех пользователей"""

    if not current_user:
        raise anauthorized_exception

    return await get_list()

from typing import List

from asyncpg import Record
from fastapi import APIRouter, Depends

from app.api.user import auth
from app.dependencies import anauthorized_exception, get_current_user
from app.models import representation
from app.services.user import get_list, get_repr

router = APIRouter(tags=["user"])
router.include_router(auth.router)


@router.get("/user")
async def user(
    username: str, current_user: representation.User | None = Depends(get_current_user)
) -> representation.User:
    if not current_user:
        raise anauthorized_exception

    return await get_repr(username)


@router.get("/user_list")
async def get_user_list(
    current_user: representation.User | None = Depends(get_current_user),
) -> list[Record]:
    if not current_user:
        raise anauthorized_exception

    return await get_list()

"""API для тегов

Мы можем только добавлять (накапливать, удалять мы не можем!)
"""

from typing import Any

from asyncpg import Record
from fastapi import APIRouter, Depends, status

from app import services
from app.dependencies import anauthorized_exception, get_current_user
from app.models.user import User

router = APIRouter(tags=["tag"])


@router.get("/tag/{id}", status_code=status.HTTP_200_OK)
async def get_tag(
    id: int,
) -> Any | None:
    """Получение тега из базы данных по ID (общедоступно)"""

    return await services.tag.get_by(id)


@router.post("/tag/{name}", status_code=status.HTTP_201_CREATED)
async def create_tag(
    name: str,
    current_user: User = Depends(get_current_user),
) -> None:
    """Создание тега в базе данных"""

    if not current_user:
        raise anauthorized_exception

    await services.tag.create(name)


@router.get("/tags", status_code=status.HTTP_200_OK)
async def get_list_tag() -> list[Record]:
    """Получение тегов из базы данных"""

    return await services.tag.get_list()

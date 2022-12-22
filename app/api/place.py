"""API для мест

Мы можем только добавлять (накапливать, удалять мы не можем!)
"""

from typing import Any

from asyncpg import Record
from fastapi import APIRouter, Depends, status

from app import services
from app.dependencies import anauthorized_exception, get_current_user
from app.models.event import Point
from app.models.user import User

router = APIRouter(tags=["place"])


@router.get("/place/{id}", status_code=status.HTTP_200_OK)
async def get_place(
    id: int,
) -> Any | None:
    """Получение места из базы данных по ID (общедоступно)"""

    return await services.place.get_by(id)


@router.post("/place/{name}", status_code=status.HTTP_201_CREATED)
async def create_place(
    point: Point,
    name: str,
    current_user: User = Depends(get_current_user),
) -> None:
    """Создание места в базе данных"""

    if not current_user:
        raise anauthorized_exception

    await services.place.create(name, point)


@router.get("/place", status_code=status.HTTP_200_OK)
async def get_list_place() -> list[Record]:
    """Получение мест из базы данных"""

    return await services.place.get_list()

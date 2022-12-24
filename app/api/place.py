"""API для мест

Мы можем только добавлять (накапливать, удалять мы не можем!)
"""

from typing import Any

from asyncpg import Record
from fastapi import APIRouter, Depends, status

from app import services
from app.dependencies import get_current_user
from app.models.place import PlaceResponse, Point
from app.models.user import User

router = APIRouter(tags=["place"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_list_place() -> list[Record]:
    """Получение мест из базы данных"""

    return await services.place.get_list()


@router.get("/{name}", status_code=status.HTTP_200_OK)
async def get_place(
    name: str,
) -> Any | None:
    """Получение места из базы данных по ID (общедоступно)"""

    return await services.place.get_by(name)


@router.post("/{name}", status_code=status.HTTP_201_CREATED)
async def create_place(
    point: Point,
    name: str,
    current_user: User = Depends(get_current_user),
) -> PlaceResponse:
    """Создание места в базе данных"""

    return await services.place.create(name, point)

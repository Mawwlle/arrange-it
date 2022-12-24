"""API для рангов"""

from typing import Any

from asyncpg import Record
from fastapi import APIRouter, Security, status

from app import services
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(tags=["rank"])


@router.post("/{rank}", status_code=status.HTTP_201_CREATED)
async def create_rank(
    rank: str,
    description: str,
    current_user: User = Security(get_current_user, scopes=["administrator"]),
) -> None:
    """Создание ранга в базе данных"""

    await services.rank.create(rank, description)


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_rank(
    id: int,
) -> Any | None:
    """Получение ранга из базы данных по ID (общедоступно)"""

    return await services.rank.get_by(id)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_list_rank() -> list[Record]:
    """Получение ранга из базы данных по ID (общедоступно)"""

    return await services.rank.get_list()


@router.delete("/{name}", status_code=status.HTTP_200_OK)
async def delete_rank(
    name: str, current_user: User = Security(get_current_user, scopes=["administrator"])
) -> None:
    """Получение ранга из базы данных по ID (общедоступно)"""

    return await services.rank.delete(name)

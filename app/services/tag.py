"""CRUD над рангами"""
from typing import Any

import asyncpg
from asyncpg import Record
from fastapi import HTTPException, status

from app.dependencies.db import database


async def create(name: str) -> None:
    """Tag creation

    :param rank: rank name
    """

    try:
        async with database.pool.acquire() as connection:
            await connection.execute('INSERT INTO "tag"("name") VALUES ($1)', name)
    except asyncpg.PostgresError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't create this tag! Already created.",
        )


async def get_by(id: int) -> Any | None:
    """Rank creation

    :param rank: rank name
    """

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetch('SELECT * FROM "tag" WHERE id=$1', id)
    return result[0]


async def get_list() -> list[Record]:
    """Rank creation

    :param rank: rank name
    """

    async with database.pool.acquire() as connection:
        return await connection.fetch('SELECT * FROM "tag"')

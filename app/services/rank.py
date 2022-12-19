"""CRUD над рангами"""
from typing import Any

from asyncpg import Record

from app.dependencies.db import database


async def create(rank: str, description: str) -> None:
    """Rank creation

    :param rank: rank name
    """

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(
                'INSERT INTO "rank"(name, description) VALUES ($1, $2)', rank, description
            )


async def get_by(id: int) -> Any | None:
    """Rank creation

    :param rank: rank name
    """

    # делается на очень скорую руку :)

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetch('SELECT * FROM "rank" WHERE id=$1', id)
    return result[0]


async def get_list() -> list[Record]:
    """Rank creation

    :param rank: rank name
    """

    async with database.pool.acquire() as connection:
        result = await connection.fetch('SELECT * FROM "rank"')
    return result


async def delete(name: str) -> None:
    """Rank creation

    :param rank: rank name
    """

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute('DELETE FROM "rank" WHERE "name"=$1', name)

"""CRUD над рангами"""
from app.dependencies.db import database


async def create(rank: str) -> None:
    """Rank creation

    :param rank: rank name
    """

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute('INSERT INTO "rank"(designation) VALUES ($1)', rank)

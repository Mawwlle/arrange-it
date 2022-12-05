from app.dependencies.db import database_pool


async def create(rank: str) -> None:
    """Role creation

    :param rank: rank name
    """

    await database_pool.execute('INSERT INTO "rank"(designation) VALUES ($1)', rank)

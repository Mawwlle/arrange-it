"""CRUD над ролями"""

from app.dependencies.db import database


async def create(role: str, description: str) -> None:
    """Role creation

    :param role: role name
    """

    async with database.pool.acquire() as connection:
        await connection.execute(
            'INSERT INTO "role"(name, description) VALUES ($1, $2)', role, description
        )

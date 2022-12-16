from app.dependencies import database


async def create(role: str) -> None:
    """Role creation

    :param role: role name
    """

    async with database.pool.acquire() as connection:
        await connection.execute('INSERT INTO "role"(name) VALUES ($1)', role)

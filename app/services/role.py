from app.dependencies import database_pool


async def create(role: str) -> None:
    """Role creation

    :param role: role name
    """

    await database_pool.execute('INSERT INTO "role"(name) VALUES ($1)', role)

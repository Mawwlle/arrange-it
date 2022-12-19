import asyncpg
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies.db import database


async def get_id_by(name: str) -> int:
    async with database.pool.acquire() as connection:
        try:
            return await connection.fetchval('SELECT "id" FROM "place" WHERE "name"=$1', name)
        except asyncpg.PostgresError as err:
            logger.error(f"Failed to get user! {repr(err)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found in database!",
            )

import asyncpg
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies import returning_id
from app.dependencies.db import database
from app.models.responses import UserResponse
from app.services.user import misc


async def create(username: str) -> UserResponse:
    """Создание администратора"""

    user_id = await misc.get_id_by(username)

    async with database.pool.acquire() as connection:
        try:
            result = await connection.fetchrow(
                'INSERT INTO "admin"("user_id") \
                    VALUES ($1) RETURNING id',
                user_id,
            )
        except asyncpg.PostgresError as err:
            logger.error(f"Failed to create admin. DUPLICATED: {repr(err)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User already admin!! {err}",
            )

    id = await returning_id(result)

    return UserResponse(message="User is admin now", username=username, id=id)


async def delete(username: str) -> UserResponse:
    """Удаление администратора"""

    user_id = await misc.get_id_by(username)

    async with database.pool.acquire() as connection:
        try:
            result = await connection.fetchrow(
                'DELETE FROM "admin" WHERE "user_id"=$1 RETURNING id',
                user_id,
            )
        except asyncpg.PostgresError as err:
            logger.error(f"Failed to create admin. DUPLICATED: {repr(err)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User already admin!! {err}",
            )

    id = await returning_id(result)

    return UserResponse(
        message=f"Admin {username} with id: {id} deleted now!", username=username, id=id
    )

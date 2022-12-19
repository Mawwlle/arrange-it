from typing import Tuple

import asyncpg
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies.db import database


async def create(file: bytes, media_type: str, event_id: int) -> int:
    """Photo creation

    :param file: picture file
    """

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            logger.debug(f"Uploading photo")
            try:
                photo_id = await connection.fetchval(
                    'INSERT INTO "photo"("photo", "media_type") VALUES ($1, $2) RETURNING id',
                    file,
                    media_type,
                )
            except asyncpg.PostgresError as err:
                logger.error(f"Failed to create event! {repr(err)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to upload picture for event!",
                )
            try:
                result = await connection.fetchval(
                    'UPDATE "event" SET "photo"=$1 WHERE "id"=$2 RETURNING id', photo_id, event_id
                )
            except asyncpg.PostgresError as err:
                logger.error(f"Failed to create event! {repr(err)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to upload picture for event!",
                )

    return int(result)


async def get(id: int) -> Tuple[bytes, str]:
    """Photo creation

    :param file: picture file
    """

    async with database.pool.acquire() as connection:
        logger.debug(f"Uploading photo")
        try:
            result = await connection.fetchval(
                'SELECT "photo", "media_type" FROM "photo" WHERE id=$1', id
            )
        except asyncpg.PostgresError as err:
            logger.error(f"Failed to create event! {repr(err)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to upload picture for event!",
            )

    return result[0], result[1]

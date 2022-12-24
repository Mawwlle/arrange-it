from datetime import datetime
from xml.dom import ValidationErr
from xml.dom.minidom import Comment

import asyncpg
from fastapi import HTTPException, status
from loguru import logger
from pydantic import ValidationError

from app.dependencies.db import database
from app.models.responses import CommentResponse


async def create(event_id: int, user_id: int, comment: str, current_datetime: datetime) -> int:
    """Comment creation function"""

    async with database.pool.acquire() as connection:
        try:
            result = await connection.fetchval(
                'INSERT INTO "comment"("date", "user", "text", "event") VALUES ($1, $2, $3, $4) RETURNING id',
                current_datetime,
                user_id,
                comment,
                event_id,
            )
        except asyncpg.PostgresError as err:
            logger.error(f"Error while fetching users {repr(err)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Failed to create comment!",
            )

    return int(result)


async def genereate_comment_from(record: asyncpg.Record) -> CommentResponse:
    try:
        return CommentResponse(
            text=record.get("text"),
            time=record.get("date"),
            user=record.get("user"),
            event=record.get("event"),
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Violation of the structure! Internal error!",
        )


async def get_by_id(id: int, event_id: int) -> CommentResponse:
    async with database.pool.acquire() as connection:
        try:
            result = await connection.fetchrow(
                'SELECT "text", "date", "user", "event" FROM "comment" WHERE id=$1 AND event=$2',
                id,
                event_id,
            )
        except asyncpg.PostgresError:
            logger.error(f"Failed to fetch comment to event by {event_id=}, {id=}!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to upload picture for event!",
            )

    return await genereate_comment_from(result)


async def get_by_event(event: int) -> list[CommentResponse]:
    async with database.pool.acquire() as connection:
        try:
            results = await connection.fetch(
                'SELECT "text", "date", "user", "event" FROM "comment" WHERE event=$1',
                event,
            )
        except asyncpg.PostgresError:
            logger.error(f"Failed to fetch comments to event: {event}!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to upload picture for event!",
            )

    return [await genereate_comment_from(result) for result in results]

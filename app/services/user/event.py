import asyncpg
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies.db import database
from app.models.subscription import SubscribtionResponse
from app.models.user import User
from app.services.user import misc


async def subscribe(user: User, event_id: int) -> SubscribtionResponse:
    """Подписка на мероприятие"""
    user_id = await misc.get_id_by(user.info.username)

    async with database.pool.acquire() as connection:
        try:
            await connection.execute(
                'INSERT INTO "user_visit_event"("user_id", "event_id") VALUES ($1, $2)',
                user_id,
                event_id,
            )
        except asyncpg.PostgresError as err:
            logger.error(f"Can't subscribe! {err}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription not succeed!",
            )

    return SubscribtionResponse(user=user_id, event=event_id, message="Subscription successfully!")


async def unsubscribe(user: User, event_id: int) -> SubscribtionResponse:
    """Отписка от мероприятия"""

    user_id = await misc.get_id_by(user.info.username)

    async with database.pool.acquire() as connection:
        try:
            await connection.execute(
                'DELETE FROM "user_visit_event" WHERE "user_id"=$1 AND "event_id"=$2',
                user_id,
                event_id,
            )
        except asyncpg.PostgresError as err:
            logger.error(f"Can't unsubscribe! {err}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can't unsubscribe!",
            )

    return SubscribtionResponse(
        user=user_id, event=event_id, message="Unsubscription successfully!"
    )


async def visited(user: User, event_id: int) -> SubscribtionResponse:
    """Посещение мероприятия"""

    user_id = await misc.get_id_by(user.info.username)

    try:
        async with database.pool.acquire() as connection:
            await connection.execute(
                'UPDATE "user_visit_event" SET "visit"=TRUE WHERE "user_id"=$1 AND "event_id"=$2',
                user_id,
                event_id,
            )
    except asyncpg.PostgresError as err:
        logger.error(f"Error while deleting user {repr(err)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not visit it!"
        )

    return SubscribtionResponse(user=user_id, event=event_id, message="Successfully. Visited now!")

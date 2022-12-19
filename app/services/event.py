"""CRUD над событиями"""

import asyncpg
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies.db import database
from app.models.event import Event
from app.services import place, user


async def create(username: str, event: Event) -> int:
    """Event creation

    :param username: organizer
    :param event: Event object
    """

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            organizer_id = await user.misc.get_id_by(username)
            place_id = await place.misc.get_id_by(name=event.place)

            logger.debug(f"organizer id: {organizer_id}")
            try:
                result = await connection.fetchval(
                    'INSERT INTO "event"("organizer", "place", "description", "date") VALUES ($1, $2, $3, $4) RETURNING id',
                    organizer_id,
                    place_id,
                    event.description,
                    event.time.replace(tzinfo=None),
                )
            except asyncpg.PostgresError as err:
                logger.error(f"Failed to create event! {repr(err)}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=err,
                ) from err

    return int(result)


async def delete(id: int) -> int:
    """Event deletion

    :param id: event id
    """

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            try:
                return await connection.fetchval(
                    'DELETE FROM "event" WHERE "id"=$1 RETURNING id', id
                )
            except asyncpg.PostgresError as err:
                logger.error(err)
                raise


async def get(id: int) -> Event:
    """Event deletion

    :param id: event id
    """

    async with database.pool.acquire() as connection:
        try:
            record = await connection.fetchrow(
                'SELECT "place", "description", "date" FROM "event" WHERE "id"=$1',
                id,
            )
        except asyncpg.PostgresError as err:
            logger.error(err)
            raise

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID: {id} not found"
        )

    place = record.get("place")
    description = record.get("description")
    time = record.get("date")

    if any(not value for value in [time, description, place]):
        raise ValueError("Incorrect value!")

    return Event(place=place, description=description, time=time)


async def get_list() -> list[asyncpg.Record]:
    """Event list"""

    async with database.pool.acquire() as connection:
        try:
            record = await connection.fetch(
                'SELECT "organizer", "place", "description", "photo", "state", "date" FROM "event"'
            )
        except asyncpg.PostgresError as err:
            logger.error(f"Error while fetching users {repr(err)}")
            return []

    return list(record)


async def get_organizer_id_by(event_id: int) -> int:
    """Getting organizer of event

    :param event_id: id of the event
    """

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            try:
                return await connection.fetchval(
                    'SELECT "organizer" FROM "event" WHERE "id"=$1', event_id
                )
            except asyncpg.PostgresError as err:
                logger.error(f"Not found in database! {err}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=err,
                ) from err

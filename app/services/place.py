"""CRUD над рангами"""
from email import message
from typing import Any

import asyncpg
from asyncpg import Record
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies.db import database
from app.models.place import PlaceResponse, Point


async def create(name: str, point: Point) -> PlaceResponse:
    try:
        async with database.pool.acquire() as connection:
            id = await connection.fetchval(
                'INSERT INTO "place"("name", "point") VALUES ($1, POINT($2, $3)) RETURNING id',
                name,
                point.x,
                point.y,
            )
    except asyncpg.PostgresError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't create this place! Already created.",
        )

    return PlaceResponse(
        id=id, name=name, point=point, message=f"Place {name} successfully created!"
    )


async def get_by(name: str) -> Any | None:
    async with database.pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow('SELECT * FROM "place" WHERE name=$1', name)
    return result


async def get_list() -> list[Record]:
    async with database.pool.acquire() as connection:
        return await connection.fetch('SELECT * FROM "place"')


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

"""CRUD над рангами"""
from typing import Any

import asyncpg
from asyncpg import Record
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies.db import database
from app.models.event import Point


async def create(name: str, point: Point) -> None:
    try:
        async with database.pool.acquire() as connection:
            await connection.execute(
                'INSERT INTO "place"("name", "point") VALUES ($1, POINT($2, $3))',
                name,
                point.x,
                point.y,
            )
    except asyncpg.PostgresError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't create this place! Already created.",
        )


async def get_by(id: int) -> Any | None:
    async with database.pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetch('SELECT * FROM "place" WHERE id=$1', id)
    return result[0]


async def get_list() -> list[Record]:
    async with database.pool.acquire() as connection:
        return await connection.fetch('SELECT * FROM "point"')


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

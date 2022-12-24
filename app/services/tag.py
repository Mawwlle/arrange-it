"""CRUD над рангами"""
from typing import Any

import asyncpg
from asyncpg import Record
from fastapi import HTTPException, status

from app.dependencies.db import database
from app.models.tag import TagResponse


async def create(name: str) -> TagResponse:
    """Tag creation

    :param rank: rank name
    """

    try:
        async with database.pool.acquire() as connection:
            id = await connection.fetchval(
                'INSERT INTO "tag"("name") VALUES ($1) RETURNING id', name
            )
    except asyncpg.PostgresError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Can't create this tag! Already created.",
        )

    return TagResponse(id=id, name=name, message="Tag created successfully!")


async def get_by(id: int) -> Any | None:
    """Rank creation

    :param rank: rank name
    """

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow('SELECT * FROM "tag" WHERE id=$1', id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found in database!"
        )

    return result


async def get_by_name(name: str) -> Any | None:
    """Rank creation

    :param rank: rank name
    """

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow('SELECT * FROM "tag" WHERE name=$1', name)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found in database!"
        )

    return result


async def get_list() -> list[Record]:
    """Rank creation

    :param rank: rank name
    """

    async with database.pool.acquire() as connection:
        return await connection.fetch('SELECT * FROM "tag"')

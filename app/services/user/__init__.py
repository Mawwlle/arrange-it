from typing import Type

import asyncpg
from asyncpg import Record
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies.db import database
from app.misc import get_password_hash
from app.models import representation


async def get_repr(username: str) -> representation.User:
    """Получение отображения пользователя из базы данных"""

    logger.info("Getting user representation")

    try:
        async with database.pool.acquire() as connection:
            record = await connection.fetchrow(
                'SELECT username, email, role, rank, name, birthday, info, interests, rating FROM "user" WHERE username = $1',
                username,
            )
    except asyncpg.PostgresError as err:
        logger.error(f"Error while getting user {err}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found!"
        ) from err

    logger.debug(record)

    return representation.User(**record)


async def get_list() -> list[Record]:
    """Получение списка пользователей"""

    try:
        async with database.pool.acquire() as connection:
            record = await database.pool.fetch(
                'SELECT username, email, name, birthday, info, interests, rating FROM "user"'
            )
    except asyncpg.PostgresError as err:
        logger.error(f"Error while fetching users {repr(err)}")
        return []

    return list(record)


async def create_user(user: representation.UserRegistration) -> int:
    """Создание пользователя в базе данных"""

    hashed_pass = await get_password_hash(user.password)

    logger.info(f"Creating user in DB: {user.username}, {user.email}")

    async with database.pool.acquire() as connection:
        try:
            result = await connection.fetchrow(
                'INSERT INTO "user"("username","password","email","name") VALUES ($1, $2, $3, $4) RETURNING id',
                user.username,
                hashed_pass,
                user.email,
                user.full_name,
            )
        except asyncpg.PostgresError as err:
            logger.error(f"Failed to create user. DUPLICATED: {repr(err)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists!",
            ) from err

    try:
        user_id = result["id"]
    except (KeyError, TypeError, ValueError) as err:
        logger.critical(err)
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail=err,
        )

    try:
        return int(user_id)
    except TypeError as err:
        logger.critical("Incorrect type of returning value")
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Possible changes in API response",
        )

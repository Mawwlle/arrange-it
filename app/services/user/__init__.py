"""CRUD операции с пользователем"""
import asyncpg
from asyncpg import Record
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies import get_password_hash, get_user_db
from app.dependencies.db import database
from app.models.responses import UserResponse
from app.models.user import User, UserRegistration


async def get_repr(username: str) -> User:
    """Получение отображения пользователя из базы данных"""

    logger.info("Getting user representation")

    user_db = await get_user_db(username)

    return User(info=user_db.info, meta=user_db.meta)


async def get_list() -> list[Record]:
    """Получение списка пользователей"""

    try:
        async with database.pool.acquire() as connection:
            record = await connection.fetch(
                'SELECT username, email, name, birthday, info, interests, rating FROM "user"'
            )
    except asyncpg.PostgresError as err:
        logger.error(f"Error while fetching users {repr(err)}")
        return []

    return list(record)


async def create(user: UserRegistration) -> int:
    """Создание пользователя в базе данных"""

    hashed_pass = await get_password_hash(user.password)

    logger.info(f"Creating user in DB: {user.info.username}, {user.info.email}")

    async with database.pool.acquire() as connection:
        try:
            result = await connection.fetchrow(
                'INSERT INTO "user"("username","password","email","name") \
                    VALUES ($1, $2, $3, $4) RETURNING id',
                user.info.username,
                hashed_pass,
                user.info.email,
                user.info.full_name,
            )
        except asyncpg.PostgresError as err:
            logger.error(f"Failed to create user. DUPLICATED: {repr(err)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists!",
            ) from err

    if not result:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Something went wrong while writing to database! ID of new entity did not created! Please try later!",
        )

    try:
        user_id = result["id"]
    except (KeyError, TypeError, ValueError) as err:
        logger.critical(err)
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail=err,
        ) from err

    try:
        return int(user_id)
    except TypeError as err:
        logger.critical("Incorrect type of returning value")
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Possible changes in API response",
        ) from err


async def delete(username: str) -> UserResponse:
    try:
        async with database.pool.acquire() as connection:
            id = await connection.fetchval(
                'DELETE FROM "user" WHERE "username"=$1 RETURNING id', username
            )
    except asyncpg.PostgresError as err:
        logger.error(f"Error while deleting user {repr(err)}")
        raise

    return UserResponse(message="User deleted successfully", username=username, id=id)


async def verify(username: str) -> UserResponse:
    try:
        async with database.pool.acquire() as connection:
            id = await connection.fetchval(
                'UPDATE "user" SET "verified"=TRUE WHERE "username"=$1 RETURNING id', username
            )
    except asyncpg.PostgresError as err:
        logger.error(f"Error while deleting user {repr(err)}")
        raise

    return UserResponse(message="User verified successfully", username=username, id=id)

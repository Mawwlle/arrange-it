"""CRUD операции с пользователем"""
import asyncpg
from asyncpg import Record
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies import get_password_hash, get_user_db, returning_id
from app.dependencies.db import database
from app.models.responses import BaseResponse, UserResponse
from app.models.user import User, UserRegistration
from app.services.user import event, misc


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

    return await returning_id(result)


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
        logger.error(f"Error while verifying user {repr(err)}")
        raise

    if not id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist!")

    return UserResponse(message="User verified successfully!", username=username, id=id)


async def verify_event(id: int) -> BaseResponse:
    try:
        async with database.pool.acquire() as connection:
            async with connection.transaction():
                id = await connection.fetchval(
                    'UPDATE "event" SET "verified"=TRUE, "state"="active"  WHERE "id"=$1 RETURNING id',
                    id,
                )
    except asyncpg.PostgresError as err:
        logger.error(f"Error while deleting user {repr(err)}")
        raise

    if not id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event does not exist!")

    return BaseResponse(message="Event verified successfully!", id=id)


async def downgrade_rating(user: User, k: int = 1, limit: int = 100) -> BaseResponse:
    query = f'UPDATE "user" SET "rating"= "rating" - {k} WHERE "id"=$1'
    user_id = await misc.get_id_by(user.info.username)
    rating = await get_rating(user_id)

    if rating <= limit:
        return BaseResponse(message="User already have lowest rating!", id=user_id)

    try:
        async with database.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(query, user_id)
    except asyncpg.PostgresError as err:
        logger.error(f"Error while upgrading user {repr(err)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist!")

    return BaseResponse(message="User downgraded successfully!", id=user_id)


async def upgrade_rating(user: int, k: int = 1, limit: int = 100) -> BaseResponse:
    query = f'UPDATE "user" SET "rating"= "rating" + {k} WHERE "id"=$1 RETURNING id'
    rating = await get_rating(user)

    if rating <= limit:
        return BaseResponse(message="User already have lowest rating!", id=user)

    try:
        async with database.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(query, user)
    except asyncpg.PostgresError as err:
        logger.error(f"Error while upgrading user {repr(err)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while upgrading user",
        )

    return BaseResponse(message="User downgraded successfully!", id=user)


async def get_rating(user_id: int) -> int:
    try:
        async with database.pool.acquire() as connection:
            rating = await connection.fetchval('SELECT "rating" FROM "user" WHERE id = $1', user_id)
    except asyncpg.PostgresError as err:
        logger.error(f"Error while getting user rating {repr(err)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist!")

    return rating

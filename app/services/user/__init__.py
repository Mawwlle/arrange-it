import asyncpg
from asyncpg import Record
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies import database_pool
from app.misc import get_password_hash
from app.models import representation


async def get_repr(username: str) -> representation.User:
    logger.info("Getting user representation")

    record = await database_pool.fetch_row(
        'SELECT username, email, role, rank, name, birthday, info, interests, rating FROM "user" WHERE username = $1',
        username,
    )

    logger.info(record)

    return representation.User(**record)


async def get_list() -> list[Record]:
    try:
        record = await database_pool.fetch(
            'SELECT username, email, name, birthday, info, interests, rating FROM "user"'
        )
    except asyncpg.PostgresError as err:
        logger.error(f"Error while fetching users {repr(err)}")
        return []

    return list(record)


async def create_user(user: representation.UserRegistration) -> None:
    hashed_pass = await get_password_hash(user.password)

    logger.info(f"Creating user in DB: {user.username}, {user.email}")

    try:
        await database_pool.execute(
            'INSERT INTO "user"("username","password","email","name") VALUES ($1, $2, $3, $4)',
            user.username,
            hashed_pass,
            user.email,
            user.full_name,
        )
    except asyncpg.PostgresError as err:
        logger.error(f"Failed to create user. DUPLICATED: {repr(err)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User already exists!",
        )

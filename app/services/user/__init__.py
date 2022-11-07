import asyncpg
from fastapi import Depends, HTTPException
from loguru import logger
from pydantic import ValidationError
from starlette import status

from app.misc import get_password_hash
from app.models import db, representation


async def get_user_repr(
    username: str, database: asyncpg.Connection = Depends(get_database)
) -> representation.User:
    record = await database.fetchrow(
        'SELECT nickname, email, name, age, info, interests, rating FROM "user" WHERE nickname = $1',
        username,
    )

    try:
        user = representation.User(**record)
    except (TypeError, ValidationError):
        logger.error("Im here")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found!"
        )

    return user


async def set_user_in_db(
    user: db.User, database: asyncpg.Connection = Depends(get_database)
) -> bool:
    hashed_pass = await get_password_hash(user.password)

    await database.execute(
        'INSERT INTO "user" VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)',
        user.id,
        user.nickname,
        hashed_pass,
        user.email,
        user.role,
        user.name,
        user.age,
        user.info,
        user.interests,
        user.rank,
        user.rating,
    )
    return True


async def get_user_list(database: asyncpg.Connection = Depends(get_database)):
    record = await database.fetch(
        'SELECT nickname, email, name, age, info, interests, rating FROM "user"'
    )

    return list(record)


async def add_user(user: db.User, database: asyncpg.Connection = Depends(get_database)):
    return await database.execute(
        'INSERT INTO "user"(nickname, password, email, role, name, age, info, interests, rank) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)',
        user.nickname,
        user.password,
        user.email,
        user.role,
        user.name,
        user.age,
        user.info,
        user.interests,
        user.rank,
    )

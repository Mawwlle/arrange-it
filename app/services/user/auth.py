from datetime import datetime, timedelta
from typing import Any

import jwt
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies import ALGORITHM, SECRET_KEY, get_user_db
from app.misc import verify_password
from app.models import representation


async def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Создание токена доступа"""

    logger.info("Start creating access token")

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    logger.debug(f"Encoded jwt: {encoded_jwt}")

    return encoded_jwt


async def authenticate_user(username: str, password: str) -> representation.User:
    """Идентификация пользователя"""

    logger.info("Starting user auth")

    user = await get_user_db(username)

    if not user:
        logger.error(f"User not found: {username} in database!")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists!",
        )

    if not await verify_password(password, user.password):
        raise ValueError("Invalid password!")

    logger.info(
        f"User: {user.username}, {user.name}, {user.email} found in database and password is correct!"
    )

    return representation.User(
        username=user.username,
        email=user.email,
        name=user.name,
        birthday=user.birthday,
        info=user.info,
        interests=user.interests,
        rating=user.rating,
        role=user.role,
        rank=user.rank,
    )

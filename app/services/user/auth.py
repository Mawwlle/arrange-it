"""Модуль отвечающий за идентификацию пользователей"""
from datetime import datetime, timedelta
from typing import Any

import jwt
from fastapi import HTTPException, status
from loguru import logger

from app.dependencies import ALGORITHM, SECRET_KEY, get_user_db, is_user_admin, verify_password
from app.models.user import User


async def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
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


async def authenticate_user(username: str, password: str, scopes: str) -> User:
    """Идентификация пользователя"""

    logger.info("Starting user auth")

    if scopes:
        authenticate_value = f'Bearer scope="{scopes}"'
    else:
        authenticate_value = "Bearer"

    user = await get_user_db(username)

    if not user:
        logger.error(f"User not found: {username} in database!")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists!",
        )

    if not await verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password!",
            headers={"WWW-Authenticate": authenticate_value},
        )

    if "administrator" in scopes:
        if not await is_user_admin(user.id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Need to be admin!",
                headers={"WWW-Authenticate": authenticate_value},
            )

    logger.info(
        f"User: \
            {user.username}, \
            {user.name}, \
            {user.email} \
        found in database and password is correct!"
    )

    return user.to_representation()

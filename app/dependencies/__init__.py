import asyncpg
import jwt
from asyncpg import Record
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from loguru import logger
from passlib.context import CryptContext
from pydantic import ValidationError
from starlette import status

from app.dependencies.db import database
from app.models import db, representation
from app.models.auth import TokenData

# Для получения такой строки:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_user_db(username: str) -> db.User:
    async with database.pool.acquire() as connection:
        async with connection.transaction():
            record = await database.pool.fetchrow(
                'SELECT * FROM "user" WHERE username = $1',
                username,
            )

    try:
        user = db.User(**record)
    except (TypeError, ValidationError) as err:
        msg = f"User not determined! Please sign up first."
        logger.error(msg)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from err

    return user


anauthorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> representation.User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        username: str = payload.get("sub")

        if username is None:
            raise anauthorized_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise anauthorized_exception

    user = await get_user_db(username=token_data.username)

    if user is None:
        raise anauthorized_exception

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

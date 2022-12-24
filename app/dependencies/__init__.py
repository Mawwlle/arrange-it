import asyncpg
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError
from loguru import logger
from passlib.context import CryptContext
from pydantic import ValidationError
from starlette import status

from app.dependencies.db import database
from app.models.auth import TokenData
from app.models.user import User, UserDB

# Для получения такой строки:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "administrator": "Administation of the platform",
    },
)


async def get_user_db(username: str) -> UserDB:
    async with database.pool.acquire() as connection:
        async with connection.transaction():
            record = await database.pool.fetchrow(
                'SELECT * FROM "user" WHERE username = $1',
                username,
            )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found in database!"
        )

    try:
        user = UserDB(**record)
    except ValidationError as error:
        logger.error(f"Can't map values from DB to models. Possibly integrity error: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Can't get user! Internal error! Possibly integrity erorr",
        )
    return user


async def is_user_admin(user_id: int) -> bool:
    async with database.pool.acquire() as connection:
        async with connection.transaction():
            record = await database.pool.fetchrow(
                'SELECT * FROM "admin" WHERE user_id = $1',
                user_id,
            )

    return bool(record)


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError, jwt.exceptions.ExpiredSignatureError):
        raise credentials_exception

    if not token_data.username:
        raise credentials_exception

    user = await get_user_db(username=token_data.username)

    if user is None:
        raise anauthorized_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user.to_representation()


async def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


anauthorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def returning_id(record: asyncpg.Record) -> int:
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while writing to database! ID of new entity did not created! Please try later!",
        )

    try:
        user_id = record["id"]
    except (KeyError, TypeError, ValueError) as err:
        logger.critical(err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err,
        )

    try:
        return int(user_id)
    except TypeError as err:
        logger.critical("Incorrect type of returning value")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Possible changes in API response",
        )

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
from app.models.user import User, UserBaseInfo, UserDBMapping, UserMetaInfo

# Для получения такой строки:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "subscriber": "Can subscribe to event",
        "administrator": "Verification",
        "organizer": "Organize events",
    },
)


async def get_user_db(username: str) -> UserDBMapping:
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
        user_base_info = UserBaseInfo(
            full_name=record.get("name"),
            username=record.get("username"),
            email=record.get("email"),
        )
        user_meta_info = UserMetaInfo(
            role=record.get("role"),
            birthday=record.get("birhday"),
            info=record.get("info"),
            interests=record.get("interests"),
            rank=record.get("rank"),
            rating=record.get("rating"),
            verified=record.get("verified"),
        )
        password = record.get("password")
        user = UserDBMapping(info=user_base_info, meta=user_meta_info, password=password)
    except (TypeError, ValidationError) as err:
        msg = f"User: {username} not determined! "
        logger.error(msg)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from err

    return user


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

    return User(info=user.info, meta=user.meta)


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
        ) from err

    try:
        return int(user_id)
    except TypeError as err:
        logger.critical("Incorrect type of returning value")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Possible changes in API response",
        ) from err

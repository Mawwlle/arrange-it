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

from app.models import db, representation
from app.models.auth import TokenData

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_user_db(username: str, database: asyncpg.Connection) -> db.User:
    record = await database.fetchrow(
        'SELECT * FROM "user" WHERE nickname = $1',
        username,
    )

    try:
        user = db.User(**record)
    except (TypeError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found!"
        )

    return user


async def get_current_user(
    database: asyncpg.Connection, token: str = Depends(oauth2_scheme)
) -> representation.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await get_user_db(username=token_data.username, database=database)

    if user is None:
        raise credentials_exception

    return representation.User(
        nickname=user.nickname,
        email=user.email,
        name=user.name,
        age=user.age,
        info=user.info,
        interests=user.interests,
        rating=user.rating,
    )


async def is_user_logged_in(current_user: representation.User | None) -> None:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


class Database:
    def __init__(
        self, user: str, password: str, host: str, database: str, port="5432"
    ) -> None:
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        self._connection_pool = None

    async def connect(self) -> None:
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=1,
                    max_size=40,
                    command_timeout=60,
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    ssl=False,
                )
                logger.info("Database pool connection opened")

            except Exception as e:
                logger.exception(e)

    async def fetch_rows(self, query: str, *args) -> Record:
        if not self._connection_pool:
            await self.connect()
        else:
            con = await self._connection_pool.acquire()

            try:
                result = await con.fetch(query, *args)
                return result
            except Exception as e:
                logger.exception(e)
            finally:
                await self._connection_pool.release(con)

    async def execute(self, query: str, *args) -> Record:
        if not self._connection_pool:
            await self.connect()
        else:
            con = await self._connection_pool.acquire()

            try:
                result = await con.execute(query, *args)
                return result
            except Exception as e:
                logger.exception(e)
            finally:
                await self._connection_pool.release(con)

    async def close(self) -> None:
        if not self._connection_pool:
            try:
                await self._connection_pool.close()
                logger.info("Database pool connection closed")
            except Exception as e:
                logger.exception(e)

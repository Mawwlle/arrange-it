from asyncio.log import logger
from typing import Any

import asyncpg
from asyncpg import Record

from app.exceptions import DBPoolConnectException
from app.settings import settings


class DatabasePool:
    def __init__(
        self, user: str, password: str, host: str, database: str, port="5432"
    ) -> None:
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        # ToDo create descriptor for it
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
            raise DBPoolConnectException(
                "Not connected. Please create connection firstly!"
            )

        logger.debug(f"New fetch query processing: {query} with args: {args}")

        con = await self._connection_pool.acquire()
        logger.debug(f"New connection to db acquired")

        try:
            result = await con.fetch(query, *args)
            return result
        except Exception as e:
            logger.exception(e)
        finally:
            await self._connection_pool.release(con)

    async def fetch_row(self, query: str, *args) -> Record:
        if not self._connection_pool:
            raise DBPoolConnectException(
                "Not connected. Please create connection firstly!"
            )

        logger.debug(f"New fetch query processing: {query} with args: {args}")

        con = await self._connection_pool.acquire()
        logger.debug(f"New connection to db acquired")

        try:
            result = await con.fetchrow(query, *args)
            return result
        except Exception as e:
            logger.exception(e)
        finally:
            await self._connection_pool.release(con)

    async def execute(self, query: str, *args: Any) -> Record:
        if not self._connection_pool:
            raise DBPoolConnectException(
                "Not connected. Please create connection firstly!"
            )

        logger.debug(f"New fetch query processing: {query} with args: {args}")

        con = await self._connection_pool.acquire()
        logger.debug(f"New connection to db acquired")

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


logger.info("Start initializing db connection pool")
database_pool = DatabasePool(
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    database=settings.POSTGRES_DB,
    host=settings.POSTGRES_SERVER,
)

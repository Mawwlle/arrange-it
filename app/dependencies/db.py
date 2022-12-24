"""Dependency which handles db issues"""
import asyncpg
from loguru import logger

from app.exceptions import DatabaseNotInitializedException
from app.settings import settings

logger.info("Start initializing db connection pool")

"""Игнорируются типы так как непонятно что тут должно быть"""


class DatabaseConnection:
    """Управление подключениями к бд"""

    __pool: asyncpg.Pool | None = None

    @property
    def pool(self) -> asyncpg.Pool:
        """Свойство для доступа к пулу коннектов"""
        if not self.__pool:
            raise DatabaseNotInitializedException("Database connection pool is not initialized!")

        return self.__pool

    async def init_pool(self) -> asyncpg.Pool:
        """Инициализация пула подключений к базе данных"""

        self.__pool = await asyncpg.create_pool(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            host=settings.POSTGRES_SERVER,
            max_size=100,
        )

        return (
            self.pool
        )  # доступ через свойство для дополнительной проверки (если не инициализация неуспешна будет ошибка)


database = DatabaseConnection()

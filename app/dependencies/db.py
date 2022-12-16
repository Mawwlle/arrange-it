"""Dependency which handles db issues"""
import asyncpg
from loguru import logger

from app.settings import settings

logger.info("Start initializing db connection pool")


class DatabaseConnection:
    """Управление подключениями к бд"""

    pool: asyncpg.Pool | None = None

    async def init_pool(self) -> asyncpg.Pool:
        """Инициализация пула подключений к базе данных"""

        self.pool = await asyncpg.create_pool(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            host=settings.POSTGRES_SERVER,
            max_size=100,
        )

        return self.pool


database = DatabaseConnection()

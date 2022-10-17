import asyncpg
import pytest


@pytest.mark.asyncio
@pytest.fixture
async def host() -> str:
    return "127.0.0.1"


@pytest.mark.asyncio
@pytest.fixture
async def password() -> str:
    return "abc"


@pytest.mark.asyncio
@pytest.fixture
async def user() -> str:
    return "postgres"


@pytest.mark.asyncio
@pytest.fixture
async def database() -> str:
    return "postgres"


@pytest.mark.asyncio
@pytest.fixture
async def db(user: str, host: str, password: str, database: str) -> asyncpg.connection.Connection:
    """ Fixture to set up the connection to database """

    conn = await asyncpg.connect(user=user, password=password,
                                 database=database, host=host)
    yield conn
    await conn.close()


@pytest.mark.asyncio
async def test_version(db: asyncpg.connection.Connection) -> None:
    # Test to make sure that there are connection is valid

    version = await db.fetch('SELECT version()')
    assert "14" in list(version[0].values())[0]

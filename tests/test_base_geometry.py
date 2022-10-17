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
@pytest.fixture
async def tags(db) -> list[str]:
    tags = ["Кинотеатр", "Аниме", "Театр"]

    await db.execute('INSERT INTO tag VALUES ($1), ($2), ($3)', tags[0], tags[1], tags[2])
    yield tags

    for tag in tags:
        await db.execute('DELETE FROM tag WHERE name = $1', tag)


@pytest.mark.asyncio
async def test_version(db: asyncpg.connection.Connection) -> None:
    # Test to make sure that there are connection is valid

    version = await db.fetch('SELECT version()')
    assert "14" in list(version[0].values())[0]


@pytest.mark.asyncio
async def test_tag_dataset(tags: list[str], db: asyncpg.connection.Connection) -> None:
    row = await db.fetch('SELECT * FROM tag')
    assert [record.get("name") for record in row] == tags

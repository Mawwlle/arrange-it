import asyncio
import asyncpg


async def run():
    conn = await asyncpg.connect(user="postgres", password="abc",
                          database="postgres", host="127.0.0.1")
    values = await conn.fetch('SELECT version()')
    record = values[0]
    print(list(record))


asyncio.get_event_loop().run_until_complete(run())

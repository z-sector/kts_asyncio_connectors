import asyncio
import os

import asyncpg


async def get_connection_by_dsn():
    """
    POSTGRES_DSN = postgres://user:password@host:port/database
    """
    return await asyncpg.connect(os.getenv("POSTGRES_DSN"))


async def get_pool_by_dsn():
    return await asyncpg.create_pool(os.getenv("POSTGRES_DSN"))


async def query(conn):
    print(await conn.fetch("select * from users"))


async def incorrect():
    conn = await get_connection_by_dsn()
    await asyncio.gather(query(conn), query(conn))


async def pool_query(pool):
    async with pool.acquire() as conn:
        await query(conn)


async def correct():
    pool = await get_pool_by_dsn()
    await asyncio.gather(pool_query(pool), pool_query(pool))


asyncio.run(correct())

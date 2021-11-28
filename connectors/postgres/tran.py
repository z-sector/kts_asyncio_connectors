import asyncio
import datetime
import os
import typing

import asyncpg


async def get_connection_by_dsn():
    """
    POSTGRES_DSN = postgres://user:password@host:port/database
    """
    return await asyncpg.connect(os.getenv("POSTGRES_DSN", "postgres://postgres:postgres@localhost:45432/postgres"))


async def insert_many(conn) -> asyncpg.Record:
    async with conn.transaction():
        for i in range(10):
            name = f'name{i}'
            await conn.execute(
                "insert into users (first_name, last_name, is_tutor, created) values ($1, $2, $3, $4)",
                name, name, True, datetime.datetime.now()
            )


async def transaction_with_error(conn):
    async with conn.transaction():
        await insert_many(conn)
        1/0


async def select_many(conn) -> typing.AsyncIterator[asyncpg.Record]:
    async with conn.transaction():
        cursor = await conn.cursor("select * from users")
        chunk = await cursor.fetch(5)
        while chunk:
            for item in chunk:
                yield item
            chunk = await cursor.fetch(5)


async def run():
    conn = await get_connection_by_dsn()
    await insert_many(conn)
    try:
        await transaction_with_error(conn)
    except ZeroDivisionError:
        pass
    async for r in select_many(conn):
        print('select_many', r)


asyncio.run(run())

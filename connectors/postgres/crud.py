import asyncio
import datetime
import os
from typing import Optional

import asyncpg


async def get_connection():
    return await asyncpg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DATABASE")
    )


async def get_connection_by_dsn():
    """
    POSTGRES_DSN = postgres://user:password@host:port/database
    """
    return await asyncpg.connect(os.getenv("POSTGRES_DSN"))


async def insert(conn) -> asyncpg.Record:
    res = await conn.fetchrow(
        "insert into users (first_name, last_name, is_tutor, created) values ($1, $2, $3, $4) returning *",
        'Alexander', 'Opryshko', True, datetime.datetime.now()
    )
    return res


async def select(conn, user_id) -> list[asyncpg.Record]:
    res = await conn.fetch("select * from users where id = $1", user_id)
    return res


async def update(conn, user_id) -> Optional[asyncpg.Record]:
    return await conn.fetchrow("update users set is_tutor = false where id = $1 returning *", user_id)


async def delete(conn, user_id) -> None:
    res = await conn.execute("delete from users where id = $1", user_id)
    print(type(res), res)


async def run():
    conn = await get_connection_by_dsn()
    res = await insert(conn)
    print('insert', res)

    user_id = res['id']
    res = await select(conn, user_id)
    print('select', res)

    res = await update(conn, user_id)
    print('update', res)

    await delete(conn, user_id)
    res = await select(conn, user_id)
    print('after delete', res)


asyncio.run(run())

from dataclasses import dataclass
from typing import Optional, Tuple

import asyncpg


@dataclass
class PgConfig:
    url: str


class Pg:
    """
    Pg класс позволяет выполнять запросы к базе данных postgres
    логику работы с базом можно было бы оставить внутри worker
    но в программировании является хорошей практикой разделять код на логические части
    поэтому взаимодействие с БД будет осуществлять через этот класс
    """
    def __init__(self, config: PgConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None

    async def setup(self):
        self.pool = await asyncpg.create_pool(self.config.url, min_size=1, max_size=1)

    async def stop(self):
        if self.pool:
            await self.pool.close()

    async def get(self, tg_id: int) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("select * from tg_users where tg_id = $1", tg_id)

    async def create(self, tg_id: int, username: str):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "insert into tg_users (tg_id, username) values ($1, $2) returning *",
                tg_id, username
            )

    async def get_or_create(self, tg_id: int, username: str) -> Tuple[dict, bool]:
        u = await self.get(tg_id)
        if u:
            return u, False
        else:
            return await self.create(tg_id, username), True


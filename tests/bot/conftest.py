import aio_pika
import asyncpg
import pytest

from bot.poller import PollerConfig
from bot.worker import BotConfig


@pytest.fixture(autouse=True)
async def purge_queue(poller_config: PollerConfig):
    conn = await aio_pika.connect(poller_config.worker_client_config.rabbit_url)
    ch = await conn.channel()
    q: aio_pika.Queue = await ch.declare_queue(poller_config.worker_client_config.queue_name)
    await q.purge()
    await conn.close()


@pytest.fixture(autouse=True)
async def truncate_tg_users(bot_config: BotConfig):
    try:
        conn = await asyncpg.connect(bot_config.pg_config.url)
        await conn.execute("truncate table tg_users")
    except:
        pass

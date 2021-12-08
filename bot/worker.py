import asyncio
import os

import aio_pika
from dataclasses import dataclass

from bot.pg import PgConfig, Pg
from clients.fapi.tg import TgClientWithFile
from clients.tg.dcs import UpdateObj
from connectors.rabbit.task.rmq_worker import Worker, WorkerConfig


@dataclass
class BotConfig:
    worker_config: WorkerConfig
    pg_config: PgConfig


class BotWorker(Worker):
    def __init__(self, token: str, config: BotConfig):
        """
        принять config
        """
        self.tg_client = TgClientWithFile(token)
        self.config = config
        self.pg = Pg(config.pg_config)
        super().__init__(config.worker_config)

    async def start(self):
        await self.pg.setup()
        return await super().start()

    async def stop(self):
        await super().stop()
        await self.pg.stop()

    async def handler(self, msg: aio_pika.IncomingMessage):
        """
        нужно переопределить метод базового класса Worker
        он должен принимать сообщения из очереди, конвертировать их в объект UpdateObj
        затем вызывать метод handle_update, в котором будет реализована бизнес-логика бота
        """
        upd = UpdateObj.Schema().loads(msg.body)
        await self.handle_update(upd)

    async def handle_update(self, upd: UpdateObj):
        user_id = upd.message.from_.id
        _, created = await self.pg.get_or_create(user_id, upd.message.from_.username)
        if created:
            await self.tg_client.send_message(upd.message.chat.id, '[greeting]')
            return
        await self.tg_client.send_message(upd.message.chat.id, '[nice to meet you]')

    """
    примечание:
    в worker мы будем работать с postgresql
    для выполнения запросов нужно сначала создать подключения (можно это сделать на старте воркера)
    для корректного завершения worker нужно закрыть подключения к postgres (можно это сделать в stop)
    """


def run_worker():
    token = os.getenv("BOT_TOKEN")
    worker_config = WorkerConfig(
        rabbit_url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"),
        queue_name="bot_poller",
        capacity=5
    )
    bot_config = BotConfig(
        worker_config=worker_config,
        pg_config=PgConfig(url=os.getenv("POSTGRES_DSN", "postgres://postgres:postgres@localhost:45432/postgres"))
    )
    worker = BotWorker(token, bot_config)

    loop = asyncio.get_event_loop()
    try:
        loop.create_task(worker.start())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(worker.stop())

import asyncio
import os

import aio_pika
from dataclasses import dataclass

from bot.pg import PgConfig
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
        raise NotImplementedError

    async def handler(self, msg: aio_pika.IncomingMessage):
        """
        нужно переопределить метод базового класса Worker
        он должен принимать сообщения из очереди, конвертировать их в объект UpdateObj
        затем вызывать метод handle_update, в котором будет реализована бизнес-логика бота
        """
        raise NotImplementedError

    async def handle_update(self, upd: UpdateObj):
        raise NotImplementedError

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
        pg_config=PgConfig(url=os.getenv("POSTGRES_DSN"))
    )
    worker = BotWorker(token, bot_config)

    loop = asyncio.get_event_loop()
    try:
        loop.create_task(worker.start())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(worker.stop())

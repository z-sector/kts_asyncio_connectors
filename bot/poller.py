import asyncio
import os
from dataclasses import dataclass

from bot.logger import BotLoggerConfig
from bot.utils import log_exceptions
from connectors.rabbit.task.rmq_worker import WorkerClientConfig


@dataclass
class PollerConfig:
    worker_client_config: WorkerClientConfig
    logger_config: BotLoggerConfig


class Poller:
    def __init__(self, token: str, config: PollerConfig):
        raise NotImplementedError

    @log_exceptions
    async def _worker(self):
        """
        нужно получать данные из tg, стоит использовать метод get_updates_in_objects (взять из предыдущего ДЗ)
        полученные сообщения нужно положить в очередь rabbitmq
        сообщения в rabbitmq нужно класть с помощью класса WorkerClient
        в очередь queue нужно класть UpdateObj
        UpdateObj нужно привести обратно к словарю, через rabbit нельзя передавать объекты
        """
        raise NotImplementedError

    async def start(self):
        """
        нужно запустить корутину _worker
        """
        raise NotImplementedError

    async def stop(self):
        """
        нужно отменить корутину _worker и дождаться ее отмены
        """
        raise NotImplementedError


def run_poller():
    token = os.getenv("BOT_TOKEN")
    config = PollerConfig(
        worker_client_config=WorkerClientConfig(
            rabbit_url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"),
            queue_name="bot_poller"
        ),
        logger_config=BotLoggerConfig(
            rabbit_url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"),
            mongo_url=os.getenv("MONGO_URL", "mongodb://root:example@localhost:27017/"),
            name="bot_logger",
        )
    )
    poller = Poller(token, config)

    loop = asyncio.get_event_loop()
    try:
        loop.create_task(poller.start())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(poller.stop())

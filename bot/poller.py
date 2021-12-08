import asyncio
import os
from dataclasses import dataclass
from typing import Optional

from bot.logger import BotLoggerConfig, BotLogger
from bot.utils import log_exceptions
from clients.fapi.tg import TgClientWithFile
from clients.tg.dcs import UpdateObj
from connectors.rabbit.task.rmq_worker import WorkerClientConfig, WorkerClient


@dataclass
class PollerConfig:
    worker_client_config: WorkerClientConfig
    logger_config: BotLoggerConfig


class Poller:
    def __init__(self, token: str, config: PollerConfig):
        self.tg_client = TgClientWithFile(token)
        self.worker_client = WorkerClient(config.worker_client_config)
        self.logger = BotLogger(config.logger_config)
        self.is_running = False
        self._task: Optional[asyncio.Task] = None

    @log_exceptions
    async def _worker(self):
        """
        нужно получать данные из tg, стоит использовать метод get_updates_in_objects (взять из предыдущего ДЗ)
        полученные сообщения нужно положить в очередь rabbitmq
        сообщения в rabbitmq нужно класть с помощью класса WorkerClient
        в очередь queue нужно класть UpdateObj
        UpdateObj нужно привести обратно к словарю, через rabbit нельзя передавать объекты
        """
        offset = 0
        while self.is_running:
            updates = await self.tg_client.get_updates_in_objects(offset=offset, timeout=60)
            for u in updates:
                offset = u.update_id + 1
                data = UpdateObj.Schema().dump(u)
                await self.logger.info('update_obj', data)
                await self.worker_client.put(data)

    async def start(self):
        """
        нужно запустить корутину _worker
        """
        self.is_running = True
        self._task = asyncio.create_task(self._worker())
        await self.logger.start()

    async def stop(self):
        """
        нужно отменить корутину _worker и дождаться ее отмены
        """
        self.is_running = False
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        await self.logger.stop()
        await self.worker_client.stop()


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

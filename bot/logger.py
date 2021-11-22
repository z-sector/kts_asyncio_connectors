import asyncio
import os
from dataclasses import dataclass

from connectors.rabbit.task.rmq_logger import Logger, LoggerConfig


@dataclass
class BotLoggerConfig(LoggerConfig):
    mongo_url: str
    mongo_db: str = "bot"


class BotLogger(Logger):
    def __init__(self, config: BotLoggerConfig):
        """
        сохранить BotLoggerConfig
        """
        raise NotImplementedError

    async def handle_info(self, payload: dict):
        """
        сохранить payload в mongo
        """
        raise NotImplementedError

    async def handle_critical(self, payload: dict):
        """
        сохранить payload в mongo
        """
        raise NotImplementedError


def run_logger():
    config = BotLoggerConfig(
        rabbit_url=os.getenv("RABBITMQ_URL"),
        mongo_url=os.getenv("MONGO_URL"),
        name="bot_logger"
    )
    logger = BotLogger(config)

    loop = asyncio.get_event_loop()
    try:
        loop.create_task(logger.start())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(logger.stop())

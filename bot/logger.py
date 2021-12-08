import asyncio
import os
from dataclasses import dataclass

from motor.motor_asyncio import AsyncIOMotorClient

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
        super().__init__(config)
        self.config = config

    async def handle_info(self, payload: dict):
        """
        сохранить payload в mongo
        """
        cli = AsyncIOMotorClient(self.config.mongo_url)
        db = cli[self.config.mongo_db]
        await db.logs.insert_one(payload)

    async def handle_critical(self, payload: dict):
        """
        сохранить payload в mongo
        """
        cli = AsyncIOMotorClient(self.config.mongo_url)
        db = cli[self.config.mongo_db]
        await db.logs.insert_one(payload)


def run_logger():
    config = BotLoggerConfig(
        rabbit_url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"),
        mongo_url=os.getenv("MONGO_URL", "mongodb://root:example@localhost:27017/"),
        name="bot_logger"
    )
    logger = BotLogger(config)

    loop = asyncio.get_event_loop()
    try:
        loop.create_task(logger.start())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(logger.stop())

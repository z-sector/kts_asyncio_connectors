import asyncio
import os

from connectors.rabbit.task.rmq_logger import Logger, LoggerConfig


class MetaclassLogger(Logger):
    def __init__(self, url: str):
        super().__init__(LoggerConfig(rabbit_url=url, name="logger_metaclass"))

    async def handle_info(self, data: dict):
        print(data)

    async def handle_critical(self, data: dict):
        print(data)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    logger = MetaclassLogger(os.getenv("RABBITMQ_URL"))
    loop.create_task(logger.start())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(logger.stop())

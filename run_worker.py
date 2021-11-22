import asyncio
import os

from aio_pika import IncomingMessage

from connectors.rabbit.task.rmq_worker import Worker, WorkerConfig


class MetaclassWorker(Worker):
    def __init__(self, rabbit_url: str):
        super().__init__(WorkerConfig(
            rabbit_url=rabbit_url,
            queue_name="worker_metaclass",
            capacity=2
        ))

    async def handler(self, msg: IncomingMessage):
        await asyncio.sleep(5)
        print(msg.body.decode())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    logger = MetaclassWorker(os.getenv("RABBITMQ_URL"))
    loop.create_task(logger.start())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(logger.stop())

import asyncio
import os

from connectors.rabbit.task.rmq_worker import WorkerClient, WorkerClientConfig


async def run():
    config = WorkerClientConfig(
        rabbit_url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"),
        queue_name="worker_metaclass",
    )
    async with WorkerClient(config) as worker:
        await worker.put({'type': 'event'})


if __name__ == "__main__":
    asyncio.run(run())

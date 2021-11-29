import asyncio
import os

from aio_pika import connect, Message


async def create_connection():
    return await connect(url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"))


async def sender():
    connection = await create_connection()
    channel = await connection.channel()
    await channel.declare_queue("ack")
    await channel.default_exchange.publish(
        Message(f"Hello World!".encode()),
        routing_key="ack",
    )
    print(" [x] Sent 'Hello World!'")
    await connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sender())

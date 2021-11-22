import asyncio
import os

from aio_pika import connect, Message, ExchangeType


async def create_connection():
    return await connect(url=os.getenv("RABBITMQ_URL"))


async def sender():
    connection = await create_connection()
    channel = await connection.channel()
    logs_exchange = await channel.declare_exchange(
        "logs", ExchangeType.FANOUT
    )
    await logs_exchange.publish(
        Message(f"Hello World!".encode()),
        routing_key="info",
    )
    print(" [x] Sent 'Hello World!'")
    await connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sender())

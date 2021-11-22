import asyncio
import os
import sys

from aio_pika import connect, Message, ExchangeType


async def create_connection():
    return await connect(url=os.getenv("RABBITMQ_URL"))


async def sender(routing_key):
    connection = await create_connection()
    channel = await connection.channel()
    logs_exchange = await channel.declare_exchange(
        "logs_level", ExchangeType.DIRECT
    )
    await logs_exchange.publish(
        Message(f"Hello World!".encode()),
        routing_key=routing_key,
    )
    print(" [x] Sent 'Hello World!'")
    await connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    rout = sys.argv[1] if len(sys.argv) > 1 else "info"
    loop.run_until_complete(sender(rout))

import asyncio
import os

from aio_pika import connect, Message, IncomingMessage


async def create_connection():
    return await connect(url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"))


async def sender():
    # Perform connection
    connection = await create_connection()

    # Creating a channel
    channel = await connection.channel()

    # Declaring queue
    await channel.declare_queue("hello")

    # Sending the message
    for i in range(2):
        await channel.default_exchange.publish(
            Message(f"{i} - Hello World!".encode()),
            routing_key="hello",
        )

    print(" [x] Sent 'Hello World!'")

    await connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sender())

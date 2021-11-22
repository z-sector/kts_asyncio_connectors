import asyncio
import os

from aio_pika import connect, IncomingMessage


async def create_connection():
    return await connect(url=os.getenv("RABBITMQ_URL"))


async def on_message(message: IncomingMessage):
    print("Before sleep!")
    async with message.process():
        await asyncio.sleep(5)
    print("After sleep!")


async def receiver():
    connection = await create_connection()
    channel = await connection.channel()
    queue = await channel.declare_queue("ack")
    await queue.consume(on_message)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(receiver())

    print(" [*] Waiting for messages.")
    loop.run_forever()

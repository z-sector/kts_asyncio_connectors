import asyncio
import os

from aio_pika import connect, IncomingMessage, ExchangeType


async def create_connection():
    return await connect(url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"))


async def on_message(message: IncomingMessage):
    async with message.process():
        await asyncio.sleep(5)
        with open('logs.txt', 'a') as fd:
            fd.write(str(message))
            fd.write('\n')


async def receiver():
    connection = await create_connection()
    channel = await connection.channel()
    logs_exchange = await channel.declare_exchange(
        "logs", ExchangeType.FANOUT
    )
    queue = await channel.declare_queue(exclusive=True)
    await queue.bind(logs_exchange)
    await queue.consume(on_message)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(receiver())

    print(" [*] Waiting for messages.")
    loop.run_forever()

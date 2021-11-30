import asyncio
import os

from aio_pika import connect, Message, IncomingMessage


async def create_connection():
    return await connect(url=os.getenv("RABBITMQ_URL", "amqp://admin:admin@localhost:45672/"))


async def on_message(message: IncomingMessage):
    """
    on_message doesn't necessarily have to be defined as async.
    Here it is to show that it's possible.
    """
    print(" [x] Received message %r" % message)
    print("Message body is: %r" % message.body)
    print("Before sleep!")
    await asyncio.sleep(5)  # Represents async I/O operations
    print("After sleep!")


async def receiver():
    # Perform connection
    connection = await create_connection()

    # Creating a channel
    channel = await connection.channel()

    # Declaring queue
    queue = await channel.declare_queue("hello")

    # Start listening the queue with name 'hello'
    await queue.consume(on_message, no_ack=True)


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
    loop.create_task(receiver())
    loop.run_until_complete(sender())

    print(" [*] Waiting for messages.")
    loop.run_forever()

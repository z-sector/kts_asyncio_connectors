import asyncio
import json
from dataclasses import dataclass
from typing import Optional

import aio_pika


@dataclass
class WorkerClientConfig:
    rabbit_url: str
    queue_name: str


class WorkerClient:
    def __init__(self, config: WorkerClientConfig):
        self.config = config
        self._connection: Optional[aio_pika.Connection] = None
        self._channel: Optional[aio_pika.Channel] = None
        self._is_ready = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def _setup(self) -> None:
        if self._is_ready:
            return None

        self._connection: aio_pika.Connection = await aio_pika.connect(url=self.config.rabbit_url)
        self._channel: aio_pika.Channel = await self._connection.channel()
        await self._channel.declare_queue(self.config.queue_name)
        self._is_ready = True

    async def put(self, data: dict):
        """
        положить сообщение с телом data в очередь с название WorkerClientConfig.queue_name
        """
        await self._setup()
        await self._channel.default_exchange.publish(
            aio_pika.Message(json.dumps(data).encode()),
            routing_key=self.config.queue_name
        )

    async def stop(self):
        """
        закрыть все ресурсы, с помощью которых работали с rabbitmq
        """
        if self._connection:
            await self._connection.close()


@dataclass
class WorkerConfig:
    rabbit_url: str
    queue_name: str
    capacity: int = 1


class Worker:
    def __init__(self, config: WorkerConfig):
        self.config = config
        self._is_ready = False
        self._is_running = False
        self._connection: Optional[aio_pika.Connection] = None
        self._channel: Optional[aio_pika.Channel] = None
        self._queue: Optional[aio_pika.Queue] = None
        self._concurrent_workers = 0
        self._stop_event = asyncio.Event()
        self._consume_tag: Optional[str] = None

    async def _setup(self):
        if self._is_ready:
            return
        self._connection = await aio_pika.connect(url=self.config.rabbit_url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=self.config.capacity)
        self._queue = await self._channel.declare_queue(self.config.queue_name)
        self._is_ready = True

    async def handler(self, msg: aio_pika.IncomingMessage):
        """
        метод, который пользователи-программисты должны переопределять в классах наследниках
        """
        print(msg)

    async def _worker(self, msg: aio_pika.IncomingMessage):
        """
        нужно вызвать метод self.handler
        если он завершился корректно, то подтвердить обработку сообщения (ack)
        """
        async with msg.process():
            self._concurrent_workers += 1
            try:
                await self.handler(msg)
            finally:
                self._concurrent_workers -= 1
                if not self._is_running and self._concurrent_workers == 0:
                    self._stop_event.set()

    async def start(self):
        """
        объявить очередь и добавить обработчик к ней
        """
        await self._setup()
        self._is_running = True
        self._consume_tag = await self._queue.consume(self._worker)

    async def stop(self):
        """
        закрыть все ресурсы, с помощью которых работали с rabbit
        """
        if self._consume_tag:
            await self._queue.cancel(self._consume_tag)
        self._is_running = False
        if self._concurrent_workers != 0:
            # self._stop_event = asyncio.Event()
            await self._stop_event.wait()
        await self._connection.close()

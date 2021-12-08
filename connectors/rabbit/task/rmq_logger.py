import json
from dataclasses import dataclass
from typing import Optional

import aio_pika
from aio_pika import ExchangeType


@dataclass
class LoggerConfig:
    rabbit_url: str
    name: str


class Logger:
    def __init__(self, config: LoggerConfig):
        self.config = config
        self._connection: Optional[aio_pika.Connection] = None
        self._channel: Optional[aio_pika.Channel] = None
        self._is_ready = False
        self._logs_exchange: Optional[aio_pika.Exchange]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def handle_info(self, payload: dict):
        """
        метод handle_info должен вызываться, когда в очередь пришло сообщение с routing_key = "info"
        """
        print(payload)

    async def handle_critical(self, payload: dict):
        """
        метод handle_critical должен вызываться, когда в очередь пришло сообщение с routing_key = "critical"
        """
        print(payload)

    async def _handle(self, message: aio_pika.IncomingMessage):
        async with message.process():
            data = json.loads(message.body)
            if message.routing_key == 'info':
                await self.handle_info(data['data'])
            elif message.routing_key == 'critical':
                await self.handle_critical(data['data'])

    async def _setup(self):
        if self._is_ready:
            return
        self._connection = await aio_pika.connect(url=self.config.rabbit_url)
        self._channel = await self._connection.channel()
        self._logs_exchange = await self._channel.declare_exchange(
            self.config.name, ExchangeType.DIRECT
        )
        self._queue = await self._channel.declare_queue(exclusive=True)
        await self._queue.bind(self._logs_exchange, routing_key="info")
        await self._queue.bind(self._logs_exchange, routing_key="critical")
        self._is_ready = True

    async def start(self):
        """
        нужно:
        - создать exchange
        - временную очереди
        - присоединить exchange к этой очереди
        - зарегистрировать consumer
        """
        await self._setup()
        await self._queue.consume(self._handle)

    async def stop(self):
        """
        закрыть все компоненты для работы с rabbitmq
        """
        await self._connection.close()

    async def info(self, msg: str, data: dict):
        """
        положить в очередь info сообщение формата
        payload = {
            "msg": msg,
            "data": data
        }
        """
        await self._setup()
        await self._logs_exchange.publish(
            aio_pika.Message(
                json.dumps({"msg": msg, "data": data}).encode()
            ),
            routing_key='info'
        )
        return 1

    async def critical(self, msg: str, data: dict):
        """
        положить в очередь critical сообщение формата
        payload = {
            "msg": msg,
            "data": data
        }
        """
        await self._setup()
        await self._logs_exchange.publish(
            aio_pika.Message(
                json.dumps({"msg": msg, "data": data}).encode()
            ),
            routing_key='critical'
        )

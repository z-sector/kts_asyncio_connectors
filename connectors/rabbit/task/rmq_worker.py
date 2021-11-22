from dataclasses import dataclass

import aio_pika


@dataclass
class WorkerClientConfig:
    rabbit_url: str
    queue_name: str


class WorkerClient:
    def __init__(self, config: WorkerClientConfig):
        self.config = config

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def put(self, data: dict):
        """
        положить сообщение с телом data в очередь с название WorkerClientConfig.queue_name
        """
        raise NotImplementedError

    async def stop(self):
        """
        закрыть все ресурсы, с помощью которых работали с rabbitmq
        """
        raise NotImplementedError


@dataclass
class WorkerConfig:
    rabbit_url: str
    queue_name: str
    capacity: int = 1


class Worker:
    def __init__(self, config: WorkerConfig):
        self.config = config

    async def handler(self, msg: aio_pika.IncomingMessage):
        """
        метод, который пользователи-программисты должны переопределять в классах наследниках
        """
        pass

    async def _worker(self, msg: aio_pika.IncomingMessage):
        """
        нужно вызвать метод self.handler
        если он завершился корректно, то подтвердить обработку сообщения (ack)
        """
        raise NotImplementedError

    async def start(self):
        """
        объявить очередь и добавить обработчик к ней
        """
        raise NotImplementedError

    async def stop(self):
        """
        закрыть все ресурсы, с помощью которых работали с rabbit
        """

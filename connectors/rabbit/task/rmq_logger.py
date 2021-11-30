from dataclasses import dataclass


@dataclass
class LoggerConfig:
    rabbit_url: str
    name: str


class Logger:
    def __init__(self, config: LoggerConfig):
        self.config = config

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def handle_info(self, payload: dict):
        """
        метод handle_info должен вызываться, когда в очередь пришло сообщение с routing_key = "info"
        """
        raise NotImplementedError

    async def handle_critical(self, payload: dict):
        """
        метод handle_critical должен вызываться, когда в очередь пришло сообщение с routing_key = "critical"
        """
        raise NotImplementedError

    async def start(self):
        """
        нужно:
        - создать exchange
        - временную очереди
        - присоединить exchange к этой очереди
        - зарегистрировать consumer
        """
        raise NotImplementedError

    async def stop(self):
        """
        закрыть все компоненты для работы с rabbitmq
        """
        raise NotImplementedError

    async def info(self, msg: str, data: dict):
        """
        положить в очередь info сообщение формата
        payload = {
            "msg": msg,
            "data": data
        }
        """
        raise NotImplementedError

    async def critical(self, msg: str, data: dict):
        """
        положить в очередь critical сообщение формата
        payload = {
            "msg": msg,
            "data": data
        }
        """
        raise NotImplementedError

import asyncio
import json
from unittest.mock import AsyncMock

import aio_pika

from connectors.rabbit.task.rmq_logger import Logger, LoggerConfig


class TestLogger:
    async def test_info(self, logger_config: LoggerConfig):
        """
        объявляем временную очередь, присоединяем ее к exchange
        после вызова logger.info ожидаем, что в нее придет сообщение
        далее вызываем logger.critical, чтобы проверить, что сообщение не пришло в очередь для info
        """
        conn = await aio_pika.connect(logger_config.rabbit_url)
        ch = await conn.channel()
        ex = await ch.declare_exchange(logger_config.name, aio_pika.ExchangeType.DIRECT)
        q: aio_pika.Queue = await ch.declare_queue(exclusive=True)
        await q.bind(ex, routing_key="info")

        data = {"info": True}
        logger = Logger(logger_config)
        await logger.info("test", data)

        msg = await q.get(no_ack=True)
        assert json.loads(msg.body) == {'data': data, 'msg': 'test'}

        await logger.critical("test", data)
        try:
            msg = await q.get(timeout=0.1)
            assert not msg
        except aio_pika.exceptions.QueueEmpty:
            pass

        await conn.close()
        await logger.stop()

    async def test_info_handler(self, logger_config: LoggerConfig):
        info_mock = AsyncMock(return_value='')
        critical_mock = AsyncMock(return_value='')

        class L(Logger):
            async def handle_info(self, data: dict):
                await info_mock()

            async def handle_critical(self, data: dict):
                await critical_mock()

        logger = L(logger_config)
        await logger.start()

        await logger.info("test", {})
        await asyncio.sleep(0.1)
        assert info_mock.called
        assert not critical_mock.called

        await logger.stop()

    async def test_critical_handler(self, logger_config: LoggerConfig):
        info_mock = AsyncMock(return_value='')
        critical_mock = AsyncMock(return_value='')

        class L(Logger):
            async def handle_info(self, data: dict):
                await info_mock()

            async def handle_critical(self, data: dict):
                await critical_mock()

        logger = L(logger_config)
        await logger.start()

        await logger.critical("test", {})
        await asyncio.sleep(0.1)
        assert not info_mock.called
        assert critical_mock.called

        await logger.stop()

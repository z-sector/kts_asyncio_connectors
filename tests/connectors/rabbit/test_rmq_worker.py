import json

import aio_pika
import asyncio
import pytest
from unittest.mock import AsyncMock

from connectors.rabbit.task.rmq_worker import Worker, WorkerClient


class TestWorkerClient:
    async def test_put(self, worker_config):
        data = {'test': True}
        async with WorkerClient(worker_config) as wc:
            await wc.put(data)
        conn = await aio_pika.connect(worker_config.rabbit_url)
        ch = await conn.channel()
        q: aio_pika.Queue = await ch.declare_queue(worker_config.queue_name)
        msg = await q.get(no_ack=True)
        assert json.loads(msg.body) == data
        await conn.close()


class TestWorker:
    async def test_handler(self, worker_config):
        mock = AsyncMock(return_value='')

        class W(Worker):
            async def handler(self, msg):
                await mock()

        worker = W(worker_config)
        await worker.start()
        async with WorkerClient(worker_config) as wc:
            await wc.put({})
        await asyncio.sleep(0.1)
        assert mock.called
        await worker.stop()

    async def test_concurrent(self, worker_config):
        """
        тест проверяет какое количество задач одновременно может обрабатывать handler
        максимальное количество параллельно обрабатываемых задач должно быть равно WorkerConfig.capacity
        """
        class W(Worker):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.concurrent = 0
                self.max_concurrent = 0

            async def handler(self, msg):
                self.concurrent += 1
                if self.concurrent > self.max_concurrent:
                    self.max_concurrent = self.concurrent
                await asyncio.sleep(0.2)
                self.concurrent -= 1

        worker = W(worker_config)
        await worker.start()
        async with WorkerClient(worker_config) as wc:
            await wc.put({})
            await wc.put({})
            await wc.put({})
            await wc.put({})
        await asyncio.sleep(0.2)
        await worker.stop()
        assert worker.max_concurrent == worker_config.capacity

    @pytest.mark.skip
    async def test_cancel(self, worker_config):
        """
        тест проверяет, что все запущенный корутины завершили свою работы и не были отменены
        если просто в Worker.stop просто вызвать await connection.close() тест не пройдет
        тест со звездочкой, поэтому необязательный, приходить его стоит, когда все остальные тесты пройдены
        """
        mock = AsyncMock(return_value='')

        class W(Worker):
            async def handler(self, msg):
                try:
                    await asyncio.sleep(0.3)
                except asyncio.CancelledError:
                    await mock()

        worker = W(worker_config)
        await worker.start()
        async with WorkerClient(worker_config) as wc:
            await wc.put({})
            await wc.put({})
        await asyncio.sleep(0.1)
        await worker.stop()
        assert not mock.called

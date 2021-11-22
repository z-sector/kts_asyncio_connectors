import asyncio
import json

import aio_pika
from aioresponses import aioresponses, CallbackResult

from bot.poller import Poller, PollerConfig

from . import data


class TestPoller:
    async def test_queue(self, tg_token, tg_base_url, poller_config: PollerConfig):
        """
        тест запускает Poller и ожидает, что новое сообщение будет положено в очередь для worker
        """
        async def cb(*_, **__):
            await asyncio.sleep(5)
            return CallbackResult(payload=data.GET_OFFSET_UPDATES)

        with aioresponses() as m:
            # сразу вернем данные о новых сообщения, в очереди должно появиться данные из data.GET_UPDATES
            m.get(tg_base_url(f'getUpdates?timeout=60'), payload=data.GET_UPDATES)
            # имитируем long polling
            m.get(tg_base_url(f'getUpdates?offset=503972236&timeout=60'), callback=cb)
            poller = Poller(tg_token, poller_config)
            await poller.start()
            await asyncio.sleep(0.1)

            try:
                # подключаемся к rabbit, чтобы получить сообщение из очереди
                conn = await aio_pika.connect(poller_config.worker_client_config.rabbit_url)
                ch = await conn.channel()
                q: aio_pika.Queue = await ch.declare_queue(poller_config.worker_client_config.queue_name)
                # получаем сообщение из очереди
                msg = await q.get(no_ack=True)
                body_dict = json.loads(msg.body)
                # сравниваем, что пришло из очереди с data.GET_UPDATES
                assert body_dict['update_id'] == data.GET_UPDATES['result'][0]['update_id']
            finally:
                await conn.close()
                await poller.stop()

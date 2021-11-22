import asyncio
from unittest.mock import patch, AsyncMock

import asyncpg
from aioresponses import aioresponses, CallbackResult

from bot.poller import PollerConfig
from bot.worker import BotWorker, BotConfig
from connectors.rabbit.task.rmq_worker import WorkerClient
from . import data


class TestWorker:
    async def test_queue(self, tg_token, tg_base_url, bot_config, poller_config: PollerConfig):
        """
        ожидаем, что если положим в очередь сообщение будет вызван метод handle_update
        """
        with patch.object(BotWorker, 'handle_update', return_value=None) as m:
            worker = BotWorker(tg_token, bot_config)
            await worker.start()
            async with WorkerClient(poller_config.worker_client_config) as wc:
                await wc.put(data.GET_UPDATES['result'][0])
                await asyncio.sleep(0.1)
                assert m.called
            await worker.stop()


class TestHandler:
    async def test_db(self, tg_token, bot_config: BotConfig, tg_base_url, update_obj):
        """
        ожидаем, что при вызове метода handle_update будет добавлена запись в БД
        """
        with aioresponses() as m:
            worker = BotWorker(tg_token, bot_config)
            await worker.start()
            m.post(tg_base_url('sendMessage'), payload=data.SEND_MESSAGE)
            await worker.handle_update(update_obj)
            await worker.stop()

        conn = await asyncpg.connect(bot_config.pg_config.url)
        res = await conn.fetchrow("select * from tg_users")
        assert res['tg_id'] == 85364161

    async def test_first_message(self, tg_token, bot_config, update_obj, tg_base_url):
        """
        ожидаем, что при первом сообщении в tg будет отправлено сообщение [greeting]
        """
        mock = AsyncMock()

        async def callback(*_, json, **__):
            await mock()
            assert 'chat_id' in json
            assert 'text' in json
            text = json['text']
            assert '[greeting]' in text
            return CallbackResult(payload=data.SEND_MESSAGE)

        with aioresponses() as m:
            worker = BotWorker(tg_token, bot_config)
            await worker.start()
            m.post(tg_base_url('sendMessage'), callback=callback)
            await worker.handle_update(update_obj)
            await worker.stop()

        assert mock.called

    async def test_second_message(self, tg_token, bot_config, update_obj, tg_base_url):
        """
        ожидаем, что при втором сообщении в tg будет отправлено сообщение отличное от [greeting]
        логика загрузки документов в s3 в тестах не проверяется
        """
        mock = AsyncMock()

        async def callback(*_, json, **__):
            await mock()
            assert 'chat_id' in json
            assert 'text' in json
            text = json['text']
            assert '[greeting]' not in text
            return CallbackResult(payload=data.SEND_MESSAGE)

        with aioresponses() as m:
            worker = BotWorker(tg_token, bot_config)
            await worker.start()
            m.post(tg_base_url('sendMessage'), payload=data.SEND_MESSAGE)
            m.post(tg_base_url('sendMessage'), callback=callback)
            await worker.handle_update(update_obj)
            await worker.handle_update(update_obj)
            await worker.stop()

        assert mock.called

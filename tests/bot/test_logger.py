import asyncio
from unittest.mock import patch

import pytest
from aioresponses import aioresponses, CallbackResult
from motor.motor_asyncio import AsyncIOMotorClient

from bot.logger import BotLogger
from bot.poller import Poller, PollerConfig
from tests.bot import data


class TestLoggerInPoller:
    async def test_logger(self, tg_token, tg_base_url, poller_config: PollerConfig):
        """
        тест запускает Poller и ожидает, что будет вызван метод BotLogger.info
        """

        async def cb(*_, **__):
            await asyncio.sleep(5)
            return CallbackResult(payload=data.GET_OFFSET_UPDATES)

        with aioresponses() as m:
            with patch.object(BotLogger, 'info', return_value=None) as info_mock:
                # сразу вернем данные о новых сообщения, в очереди должно появиться данные из data.GET_UPDATES
                m.get(tg_base_url(f'getUpdates?timeout=60'), payload=data.GET_UPDATES)
                # имитируем long polling
                m.get(tg_base_url(f'getUpdates?offset=503972236&timeout=60'), callback=cb)
                poller = Poller(tg_token, poller_config)
                await poller.start()
                await asyncio.sleep(0.1)

                assert info_mock.called

                await poller.stop()

    @pytest.fixture
    async def mongo_logs(self, poller_config: PollerConfig):
        def wrapper():
            cli = AsyncIOMotorClient(poller_config.logger_config.mongo_url)
            db = cli[poller_config.logger_config.mongo_db]
            return db.logs
        return wrapper

    @pytest.fixture(autouse=True)
    async def clean_mongo(self, poller_config, mongo_logs):
        await mongo_logs().delete_many({})

    async def test_info(self, poller_config: PollerConfig, mongo_logs):
        logger = BotLogger(poller_config.logger_config)
        await logger.handle_info({'info': True})
        res = await mongo_logs().find_one({})
        assert res['info']

    async def test_critical(self, poller_config: PollerConfig, mongo_logs):
        logger = BotLogger(poller_config.logger_config)
        await logger.handle_critical({'critical': True})
        res = await mongo_logs().find_one({})
        assert res['critical']

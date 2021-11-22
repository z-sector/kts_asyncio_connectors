import pytest

from clients.fapi.tg import TgClientWithFile
from clients.tg.api import TgClient
from clients.tg.dcs import GetUpdatesResponse
from tests.bot import data


@pytest.fixture
def tg_token():
    return '1:tg_token'


@pytest.fixture
def tg_api_url():
    return 'https://api.telegram.org'


@pytest.fixture
def tg_base_url(tg_token, tg_api_url):
    def _builder(method):
        return f'{tg_api_url}/bot{tg_token}/{method}'

    return _builder


@pytest.fixture
async def tg_client(tg_token):
    return TgClient(tg_token)


@pytest.fixture
async def file_tg_client(tg_token):
    return TgClientWithFile(tg_token)


@pytest.fixture
def update_obj():
    r: GetUpdatesResponse = GetUpdatesResponse.Schema().load(data.GET_UPDATES)
    return r.result[0]

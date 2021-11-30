from json import JSONDecodeError
from typing import Optional, List

import aiohttp
from aiohttp import ClientResponse
from marshmallow import ValidationError

from clients.base import Client
from clients.tg.dcs import UpdateObj, Message, GetUpdatesResponse, SendMessageResponse


class TgClientError(Exception):
    pass


class TgClient(Client):
    API_PATH = 'https://api.telegram.org'

    def __init__(self, token: str = ''):
        super().__init__()
        self.token = token

    def get_base_path(self) -> str:
        return f'{self.API_PATH}/bot{self.token}'

    async def _handle_response(self, resp: ClientResponse) -> dict:
        if resp.status != 200:
            raise TgClientError
        try:
            return await resp.json()
        except JSONDecodeError:
            raise TgClientError

    async def get_me(self) -> dict:
        url = self.get_base_path() + '/getMe'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await self._handle_response(resp)

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 0) -> dict:
        url = self.get_base_path() + '/getUpdates'
        params = {}

        if offset:
            params['offset'] = offset
        if timeout:
            params['timeout'] = timeout

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                return await self._handle_response(resp)

    async def get_updates_in_objects(self, *args, **kwargs) -> List[UpdateObj]:
        data = await self.get_updates(*args, **kwargs)
        try:
            resp_obj: GetUpdatesResponse = GetUpdatesResponse.Schema().load(data)
        except ValidationError:
            raise TgClientError
        return resp_obj.result

    async def send_message(self, chat_id: int, text: str) -> Message:
        url = self.get_base_path() + '/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await self._handle_response(resp)
                res: SendMessageResponse = SendMessageResponse.Schema().load(data)

        return res.result

from http.cookies import SimpleCookie
from json import JSONDecodeError
from typing import Tuple

from aiohttp import ClientResponse

from clients.base import ClientError, Client


class LmsClientError(ClientError):
    pass


class LmsClient(Client):
    BASE_PATH = 'https://lms.metaclass.kts.studio/api'

    def __init__(self, token: str):
        super().__init__()
        self.token = token

    async def _handle_response(self, resp: ClientResponse) -> Tuple[dict, ClientResponse]:
        if resp.status != 200:
            raise LmsClientError(resp, await resp.text())

        try:
            data = await resp.json()
        except JSONDecodeError:
            raise LmsClientError(resp, await resp.text())

        return data, resp

    async def get_user_current(self) -> dict:
        url = self.get_path('v2.user.current')
        data, _ = await self._perform_request('get', url, cookies={'sessionid': self.token})
        return data

    async def login(self, email: str, password: str) -> str:
        url = self.get_path('v2.user.login')
        _, resp = await self._perform_request('post', url, json={'email': email, 'password': password})

        cookies: SimpleCookie[str] = resp.cookies
        cookie_session = cookies.get('sessionid')
        if cookie_session is None:
            raise LmsClientError(resp, await resp.text())

        return cookie_session.value

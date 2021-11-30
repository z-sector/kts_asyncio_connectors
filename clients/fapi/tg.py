import aiohttp
from marshmallow import ValidationError

from clients.tg.api import TgClient, TgClientError
from clients.tg.dcs import File, Message, GetFileResponse, SendMessageResponse


class TgClientWithFile(TgClient):
    async def get_file(self, file_id: str) -> File:
        url = self.get_base_path() + '/getFile'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"file_id": file_id}) as resp:
                res = await self._handle_response(resp)
                try:
                    gf_response: GetFileResponse = GetFileResponse.Schema().load(res)
                except ValidationError:
                    raise TgClientError
                return gf_response.result

    async def download_file(self, file_path: str, destination_path: str):
        url = f'{self.API_PATH}/file/bot{self.token}/{file_path}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise TgClientError

                with open(destination_path, 'wb') as fd:
                    async for data in resp.content.iter_chunked(1024):
                        fd.write(data)

    async def send_document(self, chat_id: int, document_path) -> Message:
        url = f'{self.get_base_path()}' + '/sendDocument'
        async with aiohttp.ClientSession() as session:
            with open(document_path, 'rb') as fd:
                data = aiohttp.FormData()
                data.add_field('document', fd, content_type='text/plain')
                data.add_field('chat_id', chat_id, content_type='text/plain')
                async with session.post(url, data=data) as resp:
                    res_dict = await self._handle_response(resp)
                    try:
                        sm_response: SendMessageResponse = SendMessageResponse.Schema().load(res_dict)
                    except ValidationError:
                        raise TgClientError
                return sm_response.result


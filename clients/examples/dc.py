import asyncio
from dataclasses import field
from typing import Optional, ClassVar, Type

from marshmallow_dataclass import dataclass
from marshmallow import Schema, EXCLUDE

import aiohttp


@dataclass
class Headers:
    accept: str = field(metadata={'data_key': 'Accept'})
    accept_encoding: str = field(metadata={'data_key': 'Accept-Encoding'})
    host: str = field(metadata={'data_key': 'Host'})
    user_agent: str = field(metadata={'data_key': 'User-Agent'})
    x_amzn_trace_id: Optional[str] = field(default=None, metadata={'data_key': 'X-Amzn-Trace-Id'})

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetResponse:
    args: dict
    headers: Headers
    origin: str
    url: str

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


async def req() -> GetResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get('http://httpbin.org/get') as resp:
            data = await resp.json()
            headers_dict = data.get('headers', {})
            headers = Headers(
                accept=headers_dict['Accept'],
                accept_encoding=headers_dict['Accept-Encoding'],
                host=headers_dict['Host'],
                user_agent=headers_dict['User-Agent'],
                x_amzn_trace_id=headers_dict['X-Amzn-Trace-Id']
            )
            res = GetResponse(
                args=data['args'],
                headers=headers,
                origin=data['origin'],
                url=data['url']
            )
            print(res)
            return res


async def req_mm_dc() -> GetResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get('http://httpbin.org/get') as resp:
            data = await resp.json()
            res = GetResponse.Schema().load(data)
            print(res)
            return res


asyncio.run(req_mm_dc())

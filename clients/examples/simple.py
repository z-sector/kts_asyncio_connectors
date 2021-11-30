import asyncio

import aiohttp


async def req1():
    params = {'key1': 'value1', 'key2': 'value2'}
    async with aiohttp.ClientSession() as session:
        async with session.get('http://httpbin.org/get', params=params) as resp:
            print(await resp.read())
            print(await resp.text())
            print(await resp.json())
            print(resp.status)
            print(resp.headers)


async def req_post_json():
    params = {'key1': 'value1', 'key2': 'value2'}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://httpbin.org/post', json=params) as resp:
            print(await resp.text())


async def req_headers():
    headers = {'key1': 'value1', 'key2': 'value2'}
    cookies = {'key1': 'value1'}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://httpbin.org/post', headers=headers, cookies=cookies) as resp:
            print(await resp.text())


async def req_basic_auth():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://httpbin.org/get', auth=aiohttp.BasicAuth('user', 'pass')) as resp:
            print(await resp.text())


async def req_cookies():
    async with aiohttp.ClientSession() as session:
        await session.get('http://httpbin.org/cookies/set?my_cookie=my_value')
        filtered = session.cookie_jar.filter_cookies('http://httpbin.org')
        print(filtered)


async def req_post_file():
    async with aiohttp.ClientSession() as session:
        files = {'file': open('README.md', 'rb')}
        async with session.post('http://httpbin.org/post', data=files) as resp:
            print(await resp.json())


async def req_multipart_post():
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field('file1',
                       open('README.md', 'rb'),
                       filename='README.md',
                       content_type='text/plain')
        data.add_field('file2',
                       open('README.md', 'rb'),
                       filename='README.md',
                       content_type='text/plain')
        async with session.post('http://httpbin.org/post', data=data) as resp:
            print(await resp.json())


async def req_download_file(url: str, destination_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            with open(destination_path, 'wb') as fd:
                async for data in resp.content.iter_chunked(1024):
                    fd.write(data)


asyncio.run(req_multipart_post())

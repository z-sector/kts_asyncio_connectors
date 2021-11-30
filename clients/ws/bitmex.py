from typing import List

import aiohttp


async def fair_price_receiver(ws: aiohttp.ClientWebSocketResponse):
    async for msg in ws:
        msg: aiohttp.WSMessage
        msg_data = msg.json()
        if 'data' not in msg_data:
            continue
        for item in msg_data['data']:
            fair_price = item.get('fairPrice')
            if fair_price is not None:
                yield fair_price


async def subscribe_to_bt(ws: aiohttp.ClientWebSocketResponse):
    await ws.send_json({"op": "subscribe", "args": ["instrument:XBTUSD"]})


async def fetch_10() -> List[float]:
    session = aiohttp.ClientSession()
    ws = await session.ws_connect('wss://www.bitmex.com/realtime', autoping=True)
    await subscribe_to_bt(ws)
    res = []
    async for fp in fair_price_receiver(ws):
        res.append(fp)
        if len(res) == 10:
            break

    return res

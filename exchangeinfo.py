
import aiohttp
import asyncio
from binance import AsyncClient


async def main(loop):
    async with aiohttp.ClientSession(loop=loop) as client:
    client = await AsyncClient.create()
    exchange_info = await client.get_exchange_info()
    tickers = await client.get_all_tickers()
    print(tickers)

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))

    
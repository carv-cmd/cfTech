import logging
import asyncio
import aiohttp
from aioTraceConfig import RequestTrace
# from aiohttp.client_exceptions import ClientResponseError

logger = logging.getLogger('aioTraceConfig')


async def fetch_while(_session, url, pars):
    async with _session.get(url, params=pars, chunked=True) as response:
        # response.raise_for_status()
        _rebuild = bytearray(b"")
        while True:
            chunk = memoryview(await response.content.readany())
            if not chunk:
                break
            _rebuild += chunk
        return memoryview(_rebuild)


async def fetch_for(_session, url, pars):
    async with _session.get(url, params=pars, chunked=True) as response:
        # response.raise_for_status()
        # async for _chunk in response.content.iter_chunked(4096*4096):
        _rebuild = bytearray(b"")
        async for _chunk in response.content.iter_any():
            _rebuild += memoryview(_chunk).tobytes()
        return memoryview(_rebuild)


async def rest_client(func, endpts, params):
    _request_trace = RequestTrace()
    async with aiohttp.ClientSession(
        trace_configs=[_request_trace()], raise_for_status=True
    ) as client_sesh:
        _task_while = (asyncio.create_task(func(client_sesh, url, params)) for url in endpts)
        await asyncio.gather(*_task_while)


async def foobars(*args, ran=1, sleepy=10.0):
    logger.info(f'{args[0]}')
    for irx in range(ran):
        if irx > 0:
            await asyncio.sleep(sleepy)
        await rest_client(*args)
        logger.info(f"EOL\n")


ENDPOINTS = [
    'https://api.glassnode.com/v1/metrics/market/price_usd',
    'https://api.glassnode.com/v1/metrics/market/price_usd_close',
    'https://api.glassnode.com/v1/metrics/market/price_usd_ohlc',
    'https://api.glassnode.com/v1/metrics/market/price_drawdown_relative',
    'https://api.glassnode.com/v1/metrics/market/marketcap_usd',
    # 'https://api.glassnode.com/v1/metrics/market/mvrv_less_155',
    # 'https://api.glassnode.com/v1/metrics/market/mvrv_more_155'
]
PARAMETERS = {
    'a': 'BTC',
    'i': '24h',
    'f': 'JSON',
    'timestamp_format': 'humanized',
    'api_key': '1seRHBIi9I7zVbVFyKFdy44l33z'
}

if __name__ == '__main__':
    loops = asyncio.get_event_loop()
    loops.run_until_complete(foobars(fetch_for, ENDPOINTS, PARAMETERS))
    # loops.run_until_complete(foobars(fetch_while, ENDPOINTS, PARAMETERS))

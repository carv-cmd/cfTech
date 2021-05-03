import time
import asyncio

from pprint import pprint

from FTX_REST import FtxClient

ftx_client = FtxClient()
hold_calls = 0.25


async def ftx_single_markets(delay: float, asset: str):
    await asyncio.sleep(delay=delay)
    print(f'>>> Executing(ftx_single_markets) on: {asset}')
    return ftx_client.get_single_market(market=asset)


async def ftx_orderbook(delay: float, asset: str, depth: int = None):
    await asyncio.sleep(delay=delay)
    print(f'>>> Executing(ftx_orderbook) on: {asset}')
    return ftx_client.get_orderbook(market=asset, depth=depth)


async def ftx_trades(delay: float, asset: str,
                     limit: int = None, start: int = None, end: int = None):
    await asyncio.sleep(delay=delay)
    print(f'>>> Executing(ftx_trades) on: {asset}')
    return ftx_client.get_trades(market=asset, limit=limit, start=start, end=end)


async def ftx_public_options():
    print(f'>>> Executing(ftx_public_options)')
    return ftx_client.get_pub_options_trades()


async def ftx_options_vol():
    print(f'>>> Executing(ftx_24hr_options_vol)')
    return ftx_client.get_options_vol_24hr()


async def rest_scheduler(market, depth=20, call_hold=0.1):
    perps = f'{market}-PERP'
    mkt_usd_spot = f'{market}/USD'
    mkt_usdt_spot = f'{market}/USDT'

    perp_mkt_data = asyncio.create_task(ftx_single_markets(call_hold, perps))
    perp_orders = asyncio.create_task(ftx_orderbook(call_hold, perps, depth))
    perp_trades = asyncio.create_task(ftx_trades(call_hold, perps))

    usd_mkt_data_spot = asyncio.create_task(ftx_single_markets(call_hold, mkt_usd_spot))
    usd_orders_spot = asyncio.create_task(ftx_orderbook(call_hold, mkt_usd_spot, depth))
    usd_spot_trades = asyncio.create_task(ftx_trades(call_hold, mkt_usd_spot))

    usdt_mkt_data_spot = asyncio.create_task(ftx_single_markets(call_hold, mkt_usdt_spot))
    usdt_orders_spot = asyncio.create_task(ftx_orderbook(call_hold, mkt_usdt_spot, depth))
    usdt_spot_trades = asyncio.create_task(ftx_trades(call_hold, mkt_usdt_spot))

    public_options = asyncio.create_task(ftx_public_options())
    options_vol = asyncio.create_task(ftx_options_vol())

    print(f"\n>>> Started Tasks at: [ {time.strftime('%X')} ]")
    p_mkt = await perp_mkt_data
    usd_mkt = await usd_mkt_data_spot
    usdt_mkt = await usdt_mkt_data_spot

    p_ord = await perp_orders
    usd_ord = await usd_orders_spot
    usdt_ord = await usdt_orders_spot

    p_trades = await perp_trades
    usd_trades = await usd_spot_trades
    usdt_trades = await usdt_spot_trades

    pub_ops = await public_options
    ops_vol = await options_vol
    print(f"\nFinished Task at: [ {time.strftime('%X')} ]")

    return {'PERP': [p_mkt, p_trades, p_ord],
            'BTC/USD': [usd_mkt, usd_trades, usd_ord],
            'BTC/USDT': [usdt_mkt, usdt_trades, usdt_ord],
            'Public Options': pub_ops,
            '24hr Options Vol': ops_vol}


if __name__ == '__main__':
    foobar = asyncio.run(rest_scheduler('BTC'))

    print('\n>>> REST call responses:\n')
    pprint(foobar)

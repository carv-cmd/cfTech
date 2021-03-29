import os
from dotenv import load_dotenv, find_dotenv
import asyncio
import json
import websockets as ws

load_dotenv(find_dotenv())

# Streamer endpoint is always the following with api_key=apikey suffixed on it
url = "wss://streamer.cryptocompare.com/v2?api_key=" + os.getenv("STREAMER_SOCKET")


def set_parameters(subs, action='SubAdd'):
    """
    TODO Establish DB collection/document hierarchy model for effective management of stream ingest
    TODO Setup format string to make_example with 'type handlers'
    TODO >> if type == [0, 2, 8, 30]:   sub=f"{type}~{exchange}~{base}~{quote}'
    TODO >> if type == [24]:            sub=f"24~{exchange}~{base}~{quote}~{interval}"
    TODO >> if type == [5]:             sub=f"5~CCCAGG~{base}~{quote}'
    TODO >> if type == [11, 21]:        sub=f"{type}~{base}'
    
    [Type] [Channel]	               [Subscription]	                       [Examples]
     0	    Trade	                    0~{exchange}~{base}~{quote}	            0~Coinbase~BTC~USD
     2	    Ticker	                    2~{exchange}~{base}~{quote}	            2~Coinbase~BTC~USD
     5	    Aggregate Index (CCCAGG)    5~CCCAGG~{base}~{quote}	                5~CCCAGG~BTC~USD
     8	    Order Book L2	            8~{exchange}~{base}~{quote}	            8~Binance~BTC~USDT
     11	    Full Volume	                11~{base}	                            11~BTC
     21	    Full Top Tier Volume	    21~{base}	                            21~BTC
     24	    OHLC Candles	            24~{exchange or CCCAGG}~{base}~{quote}	24~CCCAGG~BTC~USD~m
     30	    Top of Order Book	        30~{exchange}~{base}~{quote}	        30~Coinbase~BTC~USDT

    :param subs: list of strings which are encoded as stream requests like above
    :param action: default='SubAdd' optional; 'SubRemove' to unsubscribe from stream
    :return: None, concurrently pushes json objects to MongoDB server
    """
    return {"action": action, "subs": subs}


async def keyboard_interrupt():
    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            raise SystemExit


async def cc_streamer():
    async with ws.connect(url) as websocket:
        await websocket.send(json.dumps(params))
        while True:
            try:
                data = await websocket.recv()
            except ws.ConnectionClosed:
                break
            try:
                data = json.loads(data)
                print(json.dumps(data, indent=1))
            except ValueError:
                print(data)


listed = ['0~Coinbase~BTC~USD', '5~CCCAGG~BTC~USD', '8~Binance~BTC~USDT']
params = set_parameters(subs=listed, action='SubAdd')

print(f'\nTarget URL:\n\t{url}\n')
print(f'\nRequest Parameters:\n\t{params}\n')

asyncio.run(cc_streamer())

# asyncio.get_event_loop().run_until_complete(cc_streamer())


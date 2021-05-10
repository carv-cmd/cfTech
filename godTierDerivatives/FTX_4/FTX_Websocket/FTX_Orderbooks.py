import os
import hmac
import json
import time
import zlib
from datetime import datetime
from collections import defaultdict
from itertools import zip_longest
from typing import DefaultDict, List, Dict, Tuple, Optional, Sequence

from gevent.event import Event
from dotenv import load_dotenv, find_dotenv
from FTX_Websocket import *


__all__ = [
    'FtxWebsocketClient',
    'defaultdict',
    'Optional',
    'Sequence',
    'Condition',
    'logging',
    'Thread',
    'Event',
    'Tuple',
    'List',
    'Dict',
    'Lock'
]

load_dotenv(find_dotenv())
ftx_key = os.getenv('FTX_DATA_KEY')
ftx_sec = os.getenv('FTX_DATA_SEC')


class FtxWebsocketClient(WebsocketManager):
    _ENDPOINT = 'wss://ftx.com/ws/'

    def __init__(self) -> None:
        super().__init__()
        self._api_key = ftx_key
        self._api_secret = ftx_sec
        self._orderbook_update_events: DefaultDict[str, Event] = defaultdict(Event)
        self._reset_data()

    def _reset_data(self) -> None:
        """ TODO Log.Debug when this method is called"""
        logging.debug('>>> _RESET_DATA.called(). . .')
        self._subscriptions: List[Dict] = []
        self._logged_in = False

        self._orderbooks: DefaultDict[str, Dict[str, DefaultDict[float, float]]] = \
            defaultdict(lambda: {side: defaultdict(float) for side in {'bids', 'asks'}})

        self._last_received_orderbook_data_at: float = 0.0
        self._orderbook_update_events.clear()

        self._orderbook_timestamps: DefaultDict[str, float] = defaultdict(float)
        self._orderbook_timestamps.clear()

    def _reset_orderbook(self, market: str) -> None:
        # logging.debug('>>> _RESET_ORDERBOOKS.called(). . .\n')
        if market in self._orderbooks:
            del self._orderbooks[market]
        if market in self._orderbook_timestamps:
            del self._orderbook_timestamps[market]

    def _get_url(self) -> str:
        return self._ENDPOINT

    def _on_open(self, ws):
        self._reset_data()

    def _login(self) -> None:
        ts = int(time.time() * 1000)
        self.send_json({'op': 'login', 'args': {
            'key': self._api_key,
            'sign': hmac.new(self._api_secret.encode(),
                             f'{ts}websocket_login'.encode(),
                             'sha256').hexdigest(),
            'time': ts,
        }})
        self._logged_in = True

    def _subscribe(self, subscription: Dict) -> None:
        self.send_json({'op': 'subscribe', **subscription})
        self._subscriptions.append(subscription)

    def _unsubscribe(self, subscription: Dict) -> None:
        self.send_json({'op': 'unsubscribe', **subscription})
        while subscription in self._subscriptions:
            self._subscriptions.remove(subscription)

    def _on_pong(self, ws, message):
        logging.debug('>>> PING -> PONGED')

    def _handle_orderbook_message(self, message: Dict) -> None:
        market = message['market']
        subscription = {'channel': 'orderbook', 'market': market}
        if subscription not in self._subscriptions:
            return
        data = message['data']
        if data['action'] == 'partial':
            self._reset_orderbook(market)
        for side in {'bids', 'asks'}:
            book = self._orderbooks[market][side]
            for price, size in data[side]:
                if size:
                    book[price] = size
                else:
                    del book[price]
            self._orderbook_timestamps[market] = data['time']

        checksum = data['checksum']
        orderbook = self.get_orderbook(market)
        checksum_data = [
            ':'.join([f'{float(order[0])}:{float(order[1])}'
                      for order in (bid, offer) if order])
            for (bid, offer)
            in zip_longest(orderbook['bids'][:100], orderbook['asks'][:100])
        ]
        computed_result = int(zlib.crc32(':'.join(checksum_data).encode()))
        if computed_result != checksum:
            self._last_received_orderbook_data_at = 0
            self._reset_orderbook(market)
            self._unsubscribe({'market': market, 'channel': 'orderbook'})
            self._subscribe({'market': market, 'channel': 'orderbook'})
        else:
            self._orderbook_update_events[market].set()
            self._orderbook_update_events[market].clear()

    def _on_message(self, ws, raw_message: str) -> None:
        message = json.loads(raw_message)
        message_type = message['type']
        if message_type in {'subscribed', 'unsubscribed'}:
            return
        elif message_type == 'info':
            if message['code'] == 20001:
                return self.reconnect()
        elif message_type == 'error':
            raise Exception(message)
        channel = message['channel']
        if channel == 'orderbook':
            self._handle_orderbook_message(message)

    def wait_for_orderbook_update(self, market: str, timeout: Optional[float]) -> None:
        subscription = {'channel': 'orderbook', 'market': market}
        if subscription not in self._subscriptions:
            self._subscribe(subscription)
        self._orderbook_update_events[market].wait(timeout)

    def get_orderbook(self, market: str) -> Dict[str, List[Tuple[float, float]]]:
        subscription = {'channel': 'orderbook', 'market': market}
        if subscription not in self._subscriptions:
            self._subscribe(subscription)
        if self._orderbook_timestamps[market] == 0:
            self.wait_for_orderbook_update(market, 5)
        return {
            side: sorted([(price, quantity)
                          for price, quantity in list(self._orderbooks[market][side].items())
                          if quantity], key=lambda order: order[0] * (-1 if side == 'bids' else 1)
                         ) for side in {'bids', 'asks'}
        }

    def get_orderbook_timestamp(self, market: str) -> str:
        return datetime.utcfromtimestamp(self._orderbook_timestamps[market]) \
            .strftime('%Y-%m-%d %H:%M:%S.%f')


if __name__ == '__main__':
    print(f'>>> Running FTX_ws_Client as {__name__}')

else:
    print(f'>>> Running FTX_ws_Client as {__name__}\n')

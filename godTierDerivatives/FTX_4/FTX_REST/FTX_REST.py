# REST Endpoint URL: https://ftx.com/api
# Local-Time vs FTX-Servers: https://otc.ftx.com/api/time
# from datetime import datetime
# from ciso8601 import
import os
import time
import hmac
from queue import Queue
from typing import Optional, Dict, Any, List
from requests import Request, Session, Response

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

__all__ = ['FtxClientREST', 'time', 'Dict', 'Queue']


class FtxClientREST:
    """ Local-Time vs FTX-Servers: https://otc.ftx.com/api/time """
    _ENDPOINT = 'https://ftx.com/api/'

    def __init__(self) -> None:
        # , api_key: str = None, api_secret: str = None
        self._session = Session()
        self._api_key = os.getenv('FTX_DATA_KEY')
        self._api_secret = os.getenv('FTX_DATA_SEC')
        self.response_data = Queue()

    # def _set_keys(self, api_key, api_sec):
    #     if api_key is not self._api_key:
    #         self._api_key = os.getenv('FTX_DATA_KEY')
    #     if api_sec is not self._api_secret:
    #         self._api_secret = os.getenv('FTX_DATA_SEC')

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """ TODO complete _post method """
        pass

    def _delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """ TODO complete delete method """
        pass

    def _request(self, method: str, path: str, **kwargs) -> Any:
        assert self._api_key and self._api_secret is not None, 'need keys foo'
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._authorize_request(request)
        response = self._session.send(request.prepare())
        response.close()
        return self._process_response(response)

    def _authorize_request(self, request: Request) -> None:
        timestamp = int(time.time() * 1000)
        foobar = request.prepare()
        sig_load = f"{timestamp}{foobar.method}{foobar.path_url}".encode()
        signature = hmac.new(self._api_secret.encode(), sig_load, 'sha256').hexdigest()
        request.headers = {
            'FTX-KEY': self._api_key, 'FTX-SIGN': signature, 'FTX-TS': str(timestamp)
            }

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            self.response_data.put(data['result'])
            # return data['result']

    # ################ ACCT/ORDERS ################ #
    ##################################################
    def get_account_info(self) -> dict:
        return self._get(f'account')

    def get_positions(self):
        return self._get(f'positions')

    def get_open_orders(self, market: str) -> List[dict]:
        return self._get(f'orders', {'market': market})

    def get_open_triggers(self, market: str) -> List[dict]:
        return self._get('conditional_orders', {'market': market})

    def get_trigger_triggers(self, cond_ord_id: str) -> dict:
        return self._get(f'conditional_orders/{cond_ord_id}/triggers')

    def get_trigger_history(self, market: str) -> dict:
        return self._get('conditional_orders/history', {'market': market})

    # ################## MARKETS ################## #
    ##################################################
    def list_markets(self) -> List[dict]:
        """
        Examples for each type are:
        'BTC/USD', 'BTC-PERP', 'BTC-0626', and 'BTC-MOVE-1005'.
        For futures that expired in 2019, prepend a 2019 to the date, like so:
        BTC-20190628 or BTC-MOVE-20190923.
        :return: List[dict] containing all the markets available on FTX
        """
        return self._get('markets')

    def get_single_market(self, market: str) -> List[dict]:
        """
        Get market data snapshot report on a single asset
        :param market: Market name; str('BTC-0628')
        :return: Dictionary of the assets metrics
        """
        return self._get(f'markets/{market}')

    def get_orderbook(self, market: str, depth: int = None) -> dict:
        """
        :param market: Name of the market; str('BTC-0628')
        :param depth: depth of search; int( default(20) - max(100) )
        :return: dict[list] w/ keys being; 'bid' and 'ask'
        """
        return self._get(f'markets/{market}/orderbook', {'depth': depth})

    def get_trades(self, market: str, limit: int = None, start: int = None, end: int = None) -> List:
        """
        Market is the only required param, others are optional
        :param market: Name of the market; str('BTC-0628')
        :param limit: Depth of search; int( default(20) - max(100) )
        :param start: Start time; int(1559881511)
        :param end: End time; int(1559881511)
        :return: List[dict] containing tradeID, price, time, etc
        """
        return self._get(f'markets/{market}/trades',
                         {'limit': limit,
                          'start_time': start, 'end_time': end})

    def get_historical(self,
                       market: str,
                       resolution: int,
                       limit: int = None,
                       start: int = None,
                       end: int = None) -> List[dict]:
        """
        TODO start/end_time formatting???
        :param market: Name of the market; str('BTC-0628')
        :param resolution: Interval(sec); int(15|60|300|900|3600|14400|86400)
        :param limit: depth of search int(max(5000))
        :param start: int(1559881511)
        :param end: int(1559881511)
        :return: Dictionary of historical price data
        """
        return self._get(f'markets/{market}/candles',
                         {'resolution': resolution, 'limit': limit,
                          'start_time': start, 'end_time': end})

    # ################ SPOT Margin ################ #
    ##################################################
    def spot_margin_mkt_info(self, market):
        return self._get('/spot_margin/market_info',
                         {'market': market})

    # ################## FUTURES ################## #
    ##################################################
    def list_futures(self) -> List[dict]:
        return self._get('futures')

    def get_future(self, future: str) -> dict:
        return self._get(f'futures/{future}')

    def get_future_stats(self, future: str) -> dict:
        return self._get(f'futures/{future}/stats')

    def get_funding_rates(self, start: int, end: int, future: str) -> List[dict]:
        return self._get('funding_rates',
                         {'start_time': start, 'end_time': end, 'future': future})

    def get_hist_index(self,
                       market: str,
                       resolution: int,
                       limit: int,
                       start: int,
                       end: int) -> List[dict]:
        return self._get(f'indexes/{market}/candles',
                         {'resolution': resolution, 'limit': limit,
                          'start_time': start, 'end_time': end})

    # ################## OPTIONS ################## #
    ##################################################
    def get_pub_options_trades(self) -> List[dict]:
        return self._get('options/trades')

    def get_options_fills(self,
                          start: int = None,
                          end: int = None,
                          limit: int = None) -> List[dict]:
        return self._get('options/fills',
                         {'start_time': start, 'end_time': end, 'limit': limit})

    def get_options_vol_24hr(self) -> List[dict]:
        return self._get('stats/24h_options_volume')

    def get_options_vol_hist_btc(self):
        return self._get('options/historical_volumes/BTC')

    def get_options_open_interest(self):
        return self._get('/options/open_interest/BTC')

    def get_options_hist_open_interest(self):
        return self._get('/options/historical_open_interest/BTC')


if __name__ == '__main__':
    # from pprint import pprint
    # foo = FtxClientREST()
    #
    # print('foo.')
    # print(foo.get_options_open_interest())
    print(dir(FtxClientREST))

else:
    print(f'>>> Running FTX_REST.py as {__name__}')

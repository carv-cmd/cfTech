# import json
import logging
from datetime import datetime
from threading import Thread, Lock
from _queue import Empty
from typing import *

from FTX_REST import FtxClientREST, Queue, Dict, time

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s')


class ConfigREST(FtxClientREST):
    def __init__(self, request_type: str = None, rest_request=None):
        super().__init__()
        self._rest_req = rest_request
        self._request_type = request_type
        self._request_queue = List[Any]
        self.response_data = Queue()

    def __call__(self, *args, **kwargs):
        return self._request_type

    def __getattr__(self, item):
        return self.__dict__[item]

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __get__(self, instance, owner):
        return self.__dict__['_rest_req']

    def _set_request(self, request_type: str):
        raise NotImplementedError()


class QuickData(ConfigREST):
    def __init__(self):
        super().__init__()
        self._locker = Lock()

    def _set_request(self, request_type: str):
        self.request_method = getattr(self, request_type)

    def _prep_request(self, markets: Dict[str, Optional[Any]]):
        self._request_queue = [
            [(method, pars) for pars in params] if params is not None else (method, '')
            for method, params in markets.items()]

    def _setting_request(self, sync):
        for resting in self._request_queue:
            self._set_request(resting[0][0])
            for rest in resting:
                if rest[1] is '':
                    self.response_data.put(self.request_method())
                else:
                    self.response_data.put(self.request_method(rest[1]))
                time.sleep(sync)
                self.response_data.task_done()

    def _write_responses(self):
        # logging.debug(
        #     f">>> FILENAME: ../temp_storage/REST_{metrics[0].upper()}_{market}.txt\n"
        #     f">>> DATA:REST.UPDATE:[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}]:\n"
        #     f"{data}\n")
        logging.debug('>>> _WRITE_RESPONSES.STARTED. . .')
        try:
            while True:
                # logging.debug(f'>>> Qsize({self.response_data.qsize()})')
                print(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}"
                      f'DATA: {self.response_data.get(timeout=6)}')
                # market = 'bigQuery'
                # data = self.response_data.get(timeout=6)
                # print(data)
                # metrics, data = self.response_data.get(timeout=6)
                # if metrics[1] is not None:
                #     market = ''.join(['_' if x in ['/', '-'] else x for x in metrics[1]]).upper()
                # with open(file=f"../temp_storage/REST_{metrics[0].upper()}_{market}.txt",
                #           mode='r+') as quick_save:
                #     quick_save.writelines(f"{metrics}.{market}.update("
                #                           f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')})\n"
                #                           f"{data}\n")
        except Empty:
            logging.debug(f'**** SafeWriteQueue.isEmpty(joinQueue=True) ****')
        except OSError as e:
            logging.debug(f'WHAT THE FUCKING FUCK IS THIS: {e}')

    def send_request(self, markets):
        """
        Entry Format: dict(key=str(Endpoint), value=Optional[(Endpoint.params -> None)])
        Pass multiple 'metrics' tuples where applicable to process more than one request
        Valid Endpoints Below:

        Markets:
            - "list_markets": None
            - "get_single_market": (market: str ,)
            - "get_orderbook": (market: str, depth: int)
            - "get_trades": (market: str, limit: int, start: int, end: int)
            - "get_historical": (market: str, resolution: int, limit: int, start: int, end: int)

        Options
            - "get_options_vol_24hr": None
            - "get_options_vol_hist_btc": None
            - "get_options_open_interest": None
            - "get_options_hist_open_interest": None
            - "get_pub_options_trades": None
            - "get_options_fills": (start: int, end: int, limit: int),

        Futures
            - "list_futures": None
            - "get_future": (future: str)
            - "get_future_stats": (future: str ,)
            - "get_funding_rates": (start: int, end: int, future: str)
            - "get_hist_index": (market: str, resolution: int, limit: int, start: int, end: int)

        SPOT-Margin:
            - "spot_margin_mkt_info": (market: str ,)

        Account:
            - "get_account_info": None
            - "get_positions": None
            - "get_open_orders": None
            - "get_open_triggers": None
            - "get_trigger_history": None
            - "get_trigger_triggers": None

        :return: Request.Response
        """
        # TODO -> DONT DELETE THE DOCSTRING AGAIN DUMBASS
        sync = 0.5
        prep_thread = Thread(name='_PREP', target=self._prep_request, args=(markets,))
        req_thread = Thread(name='_REQUEST', target=self._setting_request, args=(sync,))
        writes_thread = Thread(name='_RESPONSE', target=self._write_responses)
        prep_thread.start()
        req_thread.start()
        writes_thread.start()


def foobar():
    quickie = QuickData()
    quickie.send_request({
        'list_markets': (None,),
        'get_single_market': ('BTC/USD', 'ETH/USD', 'BTC-PERP', 'ETH-PERP'),
        'spot_margin_mkt_info': ('ETH/USD', 'BTC-PERP', 'ETH-PERP'),
        'get_orderbook': (('BTC/USD', '/limit=100'), )
    })


def smol_foobar():
    ftx = QuickData()
    ftx.send_request({
        # 'get_single_market': ('BTC/USD', 'ETH/USD', 'BTC-PERP', 'ETH-PERP'),
        'list_markets': None
    })

if __name__ == '__main__':
    smol_foobar()

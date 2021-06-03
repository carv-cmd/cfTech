# TIMESTAMP EXAMPLES FOR START/UNTIL INTERVALS
# Monthly resolution: 2019-05-01
#   --> Includes data from2019-05-01 00:00 UTC to 2019-05-31 23:59 UTC (i.e. May 2019)
# Weekly resolution: 2019-05-13
#   -->  Includes data from 2019-05-13 00:00 UTC to 2019-05-19 23:59 UTC (i.e. Week 20)
# Daily resolution: 2019-05-13
#   --> Includes data from2019-05-13 00:00 UTC to 2019-05-13 23:59 UTC
# Hourly resolution: 2019-05-13 10:00 UTC
#   --> Includes data from2019-05-13 10:00 UTC to 2019-05-13 10:59 UTC
# 10 Min resolution: 2019-05-13 10:20 UTC
#   --> Includes data from 2019-05-13 10:20 UTC to 2019-05-13 10:29 UTC

import os
import json
from queue import LifoQueue
from _queue import Empty
from collections import defaultdict

import pandas
import ciso8601
from pprint import pprint
from requests import Request, Session
from dotenv import load_dotenv, find_dotenv
from bson.json_util import dumps, loads

from MongoDatabase.Mongos import Any, Optional, Dict, Tuple, List
from MongoDatabase.Mongos import logging, datetime, Thread, Event, RLock
from MongoDatabase.Mongos import MongoBroker

load_dotenv(find_dotenv())

__all__ = [
    '_GlassBroker',
    '_GlassClient',
    'Glassnodes',
    'LongHandler',
    'defaultdict',
    'datetime',
    'logging',
    'pprint',
    'pandas',
    'json',
    'Optional',
    'Tuple',
    'Dict',
    'List',
    'Any'
]


class LongHandler:
    _MASK = 65536
    _DIVS, _LONGS, _MODIFY = '_divMask', '_divKeys', '_divModified'

    @staticmethod
    def _fallback_encoding(long_keys, modify, _mask=_MASK, _d=_DIVS, _k=_LONGS, _m=_MODIFY) -> Dict:
        logging.info(f'>>> ENCODING._STARTED[<{datetime.now()}>] >>>')
        _long_keys = list(long_keys)  # TODO Just pass keys as a list to begin with dipshit
        _modify_json = loads(modify)
        for elem in _modify_json:
            elem['t'] = elem['t']
            for key in (_nests for _nests in elem.keys() if _nests not in 't'):
                try:
                    elem[key] = divmod(elem[key], _mask)
                except TypeError:
                    for failed in _long_keys:
                        elem[key][failed] = divmod(elem[key][failed], _mask)
        logging.info(f'>>> ENCODING.FINISHED[<{datetime.now()}>] >>>')
        return {_d: _mask, _k: _long_keys, _m: _modify_json}

    @staticmethod
    def _fallback_decoding(modify, _d=_DIVS, _k=_LONGS, _m=_MODIFY) -> Dict:
        logging.info(f'<<< DECODING._STARTED[<{datetime.now()}>] <<<')
        _mask, _long_ki, _decode = modify['_DATA'][_d], modify['_DATA'][_k], modify['_DATA'][_m]
        for _elem in _decode:
            _elem['t'] = _elem['t']
            try:
                _div_v, _mod_v = _elem['v']
                _elem['v'] = (_div_v * _mask) + _mod_v
            except KeyError:
                for _modifier in _long_ki:
                    _div_o, _mod_o = _elem['o'][_modifier]
                    _elem['o'][_modifier] = (_div_o * _mask) + _mod_o
        logging.info(f'<<< DECODING.FINISHED[<{datetime.now()}>] <<<')
        return modify

    def glass_encoder(self, _json_decoded, _max_int64=9223372036854774783):
        _data = _json_decoded[0].json()
        _data = _data[len(_data)//2:]
        _data_key = ('v' if 'v' in _data[0] else 'o')
        logging.info(f'>>> ENCODING._STARTED[<{datetime.now()}>] >>>')
        try:
            _failed = [dict(filter(lambda elem: elem[1] > _max_int64, _data[i][_data_key].items()))
                       for i in range(0, len(_data), 500)][-1:][0]
            if any(_failed):
                _data = self._fallback_encoding(long_keys=list(_failed.keys()), modify=dumps(_data))
        except AttributeError:
            _failed = [_data[i][_data_key] for i in range(0, len(_data), 500)
                       if _data[i][_data_key] > _max_int64]
            if any(_failed):
                _data = self._fallback_encoding(long_keys=_failed, modify=dumps(_data))
        logging.info(f'>>> ENCODING.FINISHED[<{datetime.now()}>] >>>')
        return {'_metrics': _json_decoded[1], '_parameters': _json_decoded[2], '_data': _data}

    def glass_decoder(self, _json_encoded) -> Dict:
        try:
            return self._fallback_decoding(modify=_json_encoded)
        except TypeError:
            return _json_encoded
        except KeyError:
            return _json_encoded


class _GlassBroker(LongHandler, MongoBroker):
    _GLASSNODE = "https://api.glassnode.com/v1/metrics"
    _HELPER = "https://api.glassnode.com/v2/metrics/endpoints"
    _API_KEY = os.getenv('GLASSNODE')

    __slots__ = ('_session',)

    def __init__(self, start=True, ip='127.0.0.1:27017', db='Glassnodes'):
        super(_GlassBroker, self).__init__(start=start, client_ip=ip, db_name=db)
        self._session = Session()

    @staticmethod
    def ciso_handler(ts) -> str:
        """ Called implicitly when UNIX <-> UTC conversions are called by functions """
        if ts:
            return ciso8601.parse_datetime(ts).strftime('%Y-%m-%d %H:%M')

    def fallback_encoder(self, _json_decoded) -> Dict:
        """ MongoDB abstract method to guarantee proper encoding of very large nums """
        return self.glass_encoder(_json_decoded=_json_decoded)

    def fallback_decoder(self, _json_encoded) -> Dict:
        """ MongoDB abstract method to guarantee proper decoding of very large nums """
        return self.glass_decoder(_json_encoded=_json_encoded)

    def _request(self, req_method: str, target: str, params: Optional[Dict[str, Any]] = None) -> Tuple:
        """
        <GET> only method currently implemented. Handles all request.methods, I think?

        :param req_method: HTTP request method. Default(<GET>)
        :param target: Full api request endpoint. **constructed by caller
        :param params: Asset('a') required, all others autogenerated where needed

        :return: dict(key=request_endpoint, value=[asset_name, response.json])
        """
        params['api_key'] = self._API_KEY
        assert 'a' and 'api_key' in params, "MinParams=('asset'+'api_key') you fucking donkey"
        logging.info(f'* <_Request[ <{datetime.now()}> ] -> {target}')
        response = self._session.send(Request(method=req_method, url=target, params=params).prepare())
        response.close()
        _status, _reason = response.status_code, response.reason
        logging.info(f'* <Response[ <{datetime.now()}> : ({_reason} : {_status}) ]>\n')
        assert response.status_code is 200, 'Metric likely has tiered restrictions'
        return response, '_'.join(target.upper().split('/')[-2:]), params

    def get_metrics(self, index: str, endpoint: str, **kwargs) -> Tuple:
        """
        GET/Query -> https://api.glassnode.com/v1/metrics/<user>
        See _GlassClient.glass_quest docstring for all possible kwargs

        :param index: API endpoint, ex; index='indicators'
        :param endpoint: API endpoint, ex; endpoint='stock_to_flow_ratio'
        :param kwargs: {'a': AssetSymbol(required)}

        :return: tuple('index_endpoint_asset', Response)
        """
        # assert endpoint in self._validity[index], f'{index}/{endpoint} -> Invalid u fucking donkey'
        return self._request('GET', target=f'{self._GLASSNODE}/{index}/{endpoint}', params=kwargs)

    def update_endpoints(self) -> None:
        _recent = self._request('GET', target=self._HELPER, params={'a': '_null_helper'})
        self.mongo_insert_many(_recent[0].json())

    def get_endpoints(self, specified: dict, updates=False) -> List:
        """
        TODO Examples: { $and: [{"tier": 1}, {"assets.symbol": {"$eq": 'BTC'}}]}
        :param specified:
        :param updates:
        :return:
        """
        self.set_collection('GlassnodeEndpoints')
        if updates:
            self.mongo_delete()
            self.update_endpoints()
        if specified:
            _finder = self.working_col.find(specified)
        else:
            _finder = self.working_col.find()
        return list(_finder)


class _GlassClient(_GlassBroker):
    """
    * Parameters can be passed to class call or instance method.

    * Attributes stored across instances for easy subsequent requests.

    * See _GlassClient.glass_quest docstring for parameter details.

    * REQUIRED -> index: str, endpoint: str, asset_symbol['a']: str.

    * OPTIONAL -> kwargs: defaults applied on instance creation.

    * METRIC-TIMESTAMPS(utc) -> Always refer to start of interval.
    """

    __slots__ = (
        'a', 's', 'u', 'i', 'f', 'c', 'e', 'timestamp_format',
        'index', 'endpoint', 'params'
    )
    _PARAMS = __slots__[0: 8]

    def __init__(self, index=None, endpoint=None,
                 a=None, s=None, u=None, i='24h', f='JSON',
                 c=None, e=None, timestamp_format='unix'):
        super(_GlassClient, self).__init__()
        self.a = a            # asset_symbol
        self.s = s            # start_point
        self.u = u            # until_point
        self.i = i            # resolution_interval
        self.f = f            # response_format
        self.c = c            # currency
        self.e = e            # exchange_name
        self.timestamp_format = timestamp_format
        self.index = index
        self.endpoint = endpoint
        self.params = \
            {k: (self.ciso_handler(ve) if k in ('s', 'u') else ve)
             for k, ve in locals().copy().items() if k in self._PARAMS}

    def _set_attributes(self, **kwargs):
        """ Set class attributes. _PRIVATE """
        foo_copy = getattr(self, 'params').copy()
        for pos_key, pos_val in kwargs.items():
            if pos_key in 'kwargs':
                for k_key, k_val in kwargs['kwargs'].items():
                    foo_copy[k_key] = k_val
                setattr(self, 'params',
                        dict(filter(lambda elem: elem[1] is not None, foo_copy.items())))
            else:
                setattr(self, pos_key, pos_val)

    def glass_quest(self, index: str = None, endpoint: str = None, **kwargs):
        """
        See '_GlassClient.endpoint_helper' for available endpoints.

        * "index": str = ex.'indicators'
        * "endpoint": str = ex.'hash_ribbon'
        * "a": str = ex.'BTC'
        * "s": int = ISO-8601:[YYYY-MM-DD HH:MM]
        * "u": int = ISO-8601:[YYYY-MM-DD HH:MM]
        * "i": str = freq_interval(['1h', '24h', '10m', '1w', '1month'])
        * "f": str = format(['JSON', 'CSV'])
        * "c": str = currency(['NATIVE', 'USD'])
        * "e": str = ['aggregated','binance','bittrex','coinex','gate.io','huobi','poloniex']
        * "timestamp_format": str = 'unix'.try('humanized(RFC-3339)')
        * "api_key": str = autofill(see_base_class_attrs)

        :return: tuple('index_endpoint_asset', Response)
        """
        qc = locals().copy()
        if index and endpoint is not None:
            self._set_attributes(index=qc['index'], endpoint=qc['endpoint'])
        elif endpoint is not None:
            self._set_attributes(endpoint=qc['endpoint'])
        if any(qc['kwargs']):
            self._set_attributes(kwargs=qc['kwargs'])
        assert self.index and self.endpoint and self.params['a'] is not None, \
            "REQUIRED ATTRIBUTES are REQUIRED at some point. . ."
        return self.get_metrics(
            getattr(self, 'index'), getattr(self, 'endpoint'), **getattr(self, 'params'))


class Glassnodes(_GlassClient):

    __slots__ = ('_response_recv', '_rest_queue', '_mon_locker')

    def __init__(self):
        super(Glassnodes, self).__init__()
        self._response_recv = Event()
        self._rest_queue = LifoQueue()
        self._mon_locker = RLock()

    # def json_to_df(self, _metric, _data):
    #       pandas.set_option('display.width', 120)
    #     # TODO timeit (git_implementation) vs (my_implementation)
    #     #  * df = pd.DataFrame(json.loads(r.text))
    #     #  * df = df.set_index('t')
    #     #  * df.index = pd.to_datetime(df.index, unit='s')
    #     #  * df = df.sort_index()
    #     #  * s = df.v
    #     #  * s.name = '_'.join(url.split('/')[-2:])
    #     #  * return s
    #     try:
    #         frame_keys = ['t'] + list(_data[0]['o'].keys())
    #         framed = pandas.DataFrame(
    #             data=[{k: (_data[iters]['t'] if k in 't' else _data[iters]['o'][k])
    #                    for k in frame_keys} for iters in range(len(_data))],
    #             columns=frame_keys)
    #     except KeyError:
    #         framed = pandas.DataFrame(_data)
    #     framed.set_index('t', inplace=True)
    #     framed.index = pandas.to_datetime(
    #         framed.index.to_flat_index(), unit='s', infer_datetime_format=True)
    #     framed.sort_index(inplace=True)
    #     framed.name = _metric
    #     self.print_processed(framed)  # [ Comment out to disable auto printing ]
    #     self._processed.append(framed)
    #     return framed

    # def mongo_writer(self, index, endpoint, kwargs):
    #     with self._mongo_locks:
    #         dox = self.glass_quest(index=index, endpoint=endpoint, **kwargs)
    #         self.mongo_insert_one(one_dump=dox, col_name=f"{dox[2]['a'].upper()}_{dox[2]['i']}")

    def _mongo_writer(self):
        while True:
            try:
                self._response_recv.wait(timeout=6)
                dox = self._rest_queue.get_nowait()
                # self.glass_encoder(dox)  # -> test encoding schema
                self.mongo_insert_one(one_dump=dox, col_name=f"{dox[2]['a'].upper()}_{dox[2]['i']}")
                self._rest_queue.task_done()
            except Empty:
                self._rest_queue.all_tasks_done = True
                break

    def _requester(self, writer: Thread, queries: Tuple[str, str, Dict[str, Any]]):
        """ U.I. Layer, pass Tuple['idx', 'endpoint', Dict:[str(param), Any]] """
        with self._mon_locker:
            self._rest_queue.put(self.glass_quest(index=queries[0], endpoint=queries[1], **queries[2]))
        try:
            writer.start()
        except RuntimeError:
            pass
        self._response_recv.set()
        self._response_recv.clear()

    # def _mongo_reader(self):
    #     pass
    #
    # def _loader(self):
    #     pass

    def magic_metrics(self, big_query: List[Tuple[str, str, Dict[str, Any]]]):
        _mon_writes = Thread(name='_MONGO_WRITER', target=self._mongo_writer)
        for query in big_query:
            try:
                raise FileNotFoundError()
            except FileNotFoundError:
                _threader = Thread(name='_REQUESTS', target=self._requester, args=(_mon_writes, query,))
                _threader.start()
        with self._mon_locker:
            self._rest_queue.join()
            self._response_recv.set()
            self.kill_client()


def push_mongo(mons: Glassnodes):
    # ('mining', 'difficulty_mean', {'a': 'BTC'}) wildly overFlows
    _rapid = [
        # ('addresses', 'count', {'a': 'BTC'}),
        # ('addresses', 'sending_count', {'a': 'BTC'}),
        # ('addresses', 'receiving_count', {'a': 'BTC'}),
        # ('addresses', 'active_count', {'a': 'BTC'}),
        # ('addresses', 'new_non_zero_count', {'a': 'BTC'}),
        # ('market', 'price_usd_close', {'a': 'BTC'}),
        # ('market', 'marketcap_realized_usd', {'a': 'BTC'}),
        # ('market', 'price_drawdown_relative', {'a': 'BTC'}),
        # ('market', 'marketcap_usd', {'a': "BTC"}),
        # ('market', 'mvrv_z_score', {'a': "BTC"}),
        # ('market', 'price_usd_ohlc', {'a': "BTC"}),
        # ('market', 'price_realized_usd', {'a': "BTC"}),
        # ('supply', 'active_more_1y_percent', {'a': 'BTC'}),
        # ('supply', 'current', {'a': 'BTC'}),
        # ('blockchain', 'block_height', {'a': 'BTC'}),
        # ('indicators', 'sopr', {'a': 'BTC'}),
        # ('indicators', 'stock_to_flow_ratio', {'a': 'BTC'}),
        # ('indicators', 'hash_ribbon', {'a': 'BTC'}),
        # ('indicators', 'difficulty_ribbon', {'a': 'BTC'}),
        # ('indicators', 'realized_profit', {'a': 'BTC'}),
        # ('indicators', 'realized_loss', {'a': 'BTC'}),
        # ('indicators', 'reserve_risk', {'a': 'BTC'}),
        # ('transactions', 'rate', {'a': 'BTC'}),
        # ('transactions', 'count', {'a': 'BTC'}),
        # ('transactions', 'size_mean', {'a': 'BTC'}),
        # ('transactions', 'size_sum', {'a': 'BTC'}),
        # ('transactions', 'transfers_volume_sum', {'a': 'BTC'}),
        # ('transactions', 'transfers_volume_mean', {'a': 'BTC'}),
        ('transactions', 'transfers_volume_median', {'a': 'BTC'}),
    ]
    mons.magic_metrics(_rapid)


def pull_mongo(mons: Glassnodes):
    mons.set_collection('BTC_24h')
    result = mons.mongo_query(metrics=f'market_mvrv_score')
    print(result[0])


def endpoints(glassed: Glassnodes, tier: int = 1, asset: str = 'BTC', update=False):
    foo_bar = glassed.get_endpoints(
        specified={'$and': [{"tier": tier}, {"assets.symbol": {"$eq": asset.upper()}}]},
        updates=update)
    glassed.kill_client()
    for fb in foo_bar:
        print(fb)
        # print(fb['path'], fb['assets']['tags'])
        break


def endpoint_queries(mons: Glassnodes,
    tier: int = None, asset: str = None, currencies: str = None, json_csv: str = None
):
    # print(locals())
    mons.set_collection('GlassnodeEndpoints')
    quick = {'tier': 1, 'asset': 'BTC', 'currencies': 'NATIVE', 'formatting': 'JSON'}
    to_load = {
        '$and': [
            {"tier": quick['tier']},
            {"assets.symbol": {"$eq": quick['asset'].upper()}}
        ]
    }
    print(mons.mongo_query(user_defined=to_load))
    pass


if __name__ == '__main__':
    glasses = Glassnodes()
    endpoint_queries(glasses)
    # endpoints(glasses)
    # push_mongo(glasses)
    # pull_mongo(glasses)
    pass


else:
    logging.debug(f'>>> Initialized {__name__} @ <{datetime.now()}>\n')

# TODO Why are below metrics restricted(status:403)?
#   * ('market', 'mvrv_less_155', {'a': "BTC"}),
#   * ('market', 'mvrv_more_155', {'a': "BTC"}),

# TODO Verify all these mfs format properly
# _non_standard_responses = (
#     'futures_funding_rate_perpetual_all',
#     'futures_volume_daily_sum_all',
#     'futures_volume_daily_perpetual_sum_all',
#     'futures_open_interest_sum_all',
#     'futures_open_interest_perpetual_sum_all',
#     'futures_open_interest_latest',
#     'futures_volume_daily_latest',
#     'balance_exchanges_all',
#     'balance_miners_all',
#     'supply_distribution_relative',
#     'exchanges_sum',
#     'exchanges_relative',
#     'exchanges_mean',
#     'hash_ribbon',
#     'difficulty_ribbon',
#     'spent_output_price_distribution_ath',
#     'spent_output_price_distribution_percent',
#     'cyd',
#     'cyd_supply_adjusted',
#     'cyd_account_based_supply_adjusted',
#     'cyd_account_based', 'cdd90_age_adjusted',
#     'cdd90_account_based_age_adjusted',
#     'stock_to_flow_ratio',
#     'utxo_realized_price_distribution_ath',
#     'utxo_realized_price_distribution_percent',
#     'soab',
#     'price_usd_ohlc',
#     'liquid_illiquid_sum',
#     'hodl_waves',
#     'rcap_hodl_waves',
#     'lth_sth_profit_loss_relative',
#     'transfers_volume_miners_to_exchanges_all',
#     'supply_distribution_relative'
# )

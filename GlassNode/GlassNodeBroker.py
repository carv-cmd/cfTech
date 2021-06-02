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
    'GlassClient',
    'Glassnodes',
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
    def _fallback_encoding(long_keys, modify_json,_mask=_MASK, _d=_DIVS, _k=_LONGS, _m=_MODIFY) -> Dict:
        assert any(long_keys), '_LONG_KEY_CHECK_'
        logging.info(f'>>> ENCODING._STARTED[<{datetime.now()}>] >>>')
        _long_keys = list(long_keys.keys())  # TODO Just pass keys as a list to begin with dipshit
        _modify_json = loads(modify_json)
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
        _mask, _long_ki, _decode = modify['_DATA_'][_d], modify['_DATA_'][_k], modify['_DATA_'][_m]
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
        _data, _path, _params = _json_decoded
        _data = _data.json()
        _data_keys = list(_data[0].keys())[1]
        try:
            # _fuzzy = [i for i in range(0, len(_data), 500)]
            fuzz = [dict(filter(lambda elem: elem[1] > _max_int64, _data[i][_data_keys].items()))
                           for i in range(0, len(_data), 500)][-1:][0]
            _data = self._fallback_encoding(
                long_keys=fuzz,
                modify_json=dumps(_data))
        except AssertionError:
            pass
        except AttributeError:
            # print('>>> RAISED ATTRIBUTE ERROR!!!')
            pass
        return {'_METRIC_': _path, '_PARAMS_': _params, '_DATA_': _data}

    def glass_decoder(self, _json_encoded):
        try:
            return self._fallback_decoding(modify=_json_encoded)
        except TypeError:
            return _json_encoded


class _GlassBroker(LongHandler, MongoBroker):
    _GLASSNODE = "https://api.glassnode.com/v1/metrics"
    _HELPER = "https://api.glassnode.com/v2/metrics/endpoints"
    _API_KEY = os.getenv('GLASSNODE')

    __slots__ = ('_session',)

    def __init__(self, start=True, ip='127.0.0.1:27017', db='Glassnodes'):
        super(_GlassBroker, self).__init__(start=start, client_ip=ip, db_name=db)
        self._session = Session()
        # self._validity = self._load_valid_endpoints()

    def _load_valid_endpoints(self):
        # TODO Load valid endpoints into a dictionary for assertion reference
        # TODO _loads_valid_endpoints_ = json.loads(mong.query(_check_valid))
        pass

    @staticmethod
    def ciso_handler(ts):
        """ Called implicitly when UNIX <-> UTC conversions are called by functions """
        if ts:
            return ciso8601.parse_datetime(ts).strftime('%Y-%m-%d %H:%M')

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
        logging.info(f'* <_Request[ <{datetime.now()}> ] -> {target}\n** ?params={params}')
        response = self._session.send(Request(method=req_method, url=target, params=params).prepare())
        response.close()
        _status, _reason = response.status_code, response.reason
        logging.info(f'* <Response[ <{datetime.now()}> : ({_status}:{_reason}) ]>\n')
        assert response.status_code is 200, 'Metric likely has tiered restrictions'
        return response, '_'.join(target.upper().split('/')[-2:]), params

    def get_metrics(self, index: str, endpoint: str, **kwargs) -> tuple:
        """
        GET/Query -> https://api.glassnode.com/v1/metrics/<user>
        See GlassClient.glass_quest docstring for all possible kwargs

        :param index: API endpoint, ex; index='indicators'
        :param endpoint: API endpoint, ex; endpoint='stock_to_flow_ratio'
        :param kwargs: {'a': AssetSymbol(required)}

        :return: tuple('index_endpoint_asset', Response)
        """
        # assert endpoint in self._validity[index], f'{index}/{endpoint} -> Invalid u fucking donkey'
        return self._request('GET', target=f'{self._GLASSNODE}/{index}/{endpoint}', params=kwargs)

    def get_endpoints(self, path=True, tier=False, assets=False) -> List:
        """
        Query all known glassnode endpoints and their optional parameters
        Internals are absolute heavy wizardry, see the raw response obj for clarity

        :param path: Get endpoint *omitting glassnode.api prefix
        :param tier: Get subscription tier required for unrestricted calls
        :param assets: Get available assets for given endpoint

        :return: None, prints results
        """
        locals_copy = locals().copy()
        del locals_copy['self']
        response = self._request('GET', target=self._HELPER, params={'a': '_null_helper'})
        response = response[0].json()
        return response

    def fallback_encoder(self, _json_decoded):
        return self.glass_encoder(_json_decoded=_json_decoded)

    def fallback_decoder(self, _json_encoded):
        return self.glass_decoder(_json_encoded=_json_encoded)


class GlassClient(_GlassBroker):
    """
    * Parameters can be passed to class call or instance method.

    * Attributes stored across instances for easy subsequent requests.

    * See GlassClient.glass_quest docstring for parameter details.

    * REQUIRED -> index: str, endpoint: str, asset_symbol['a']: str.

    * OPTIONAL -> kwargs: defaults applied on instance creation.

    * METRIC-TIMESTAMPS(utc) -> Always refer to start of interval.
    """

    __slots__ = ('a', 's', 'u', 'i', 'f', 'c', 'e', 'timestamp_format', 'index', 'endpoint', 'params')
    _PARAMS = __slots__[0: 8]

    def __init__(self, index=None, endpoint=None,
                 a=None, s=None, u=None, i='24h', f='JSON',
                 c=None, e=None, timestamp_format='unix'):
        super(GlassClient, self).__init__()
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
        See 'GlassClient.endpoint_helper' for available endpoints.

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


class Glassnodes(GlassClient):
    # Pandas.DataFrame Configuration
    pandas.set_option('display.width', 120)

    __slots__ = ('_mongo_locks', '_request_complete', '_results_ready')

    def __init__(self):
        super(Glassnodes, self).__init__()
        self._mongo_locks = RLock()
        # self._request_complete = Event()
        self._results_ready = Event()

    # def json_to_df(self, _metric, _data):
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
    #
    # def get_processed(self) -> List:
    #     return self._processed
    #
    # @staticmethod
    # def print_processed(ready) -> None:
    #     """ DataFrame pretty printer """
    #     _line = ''.join(['-' for i in range(50)])
    #     _formatter = "{}\npandas.DataFrame -> {}\n\n{}\n\n{}\n{}"
    #     try:
    #         print(_formatter.format('\n'+_line, ready.name, ready, ready.columns, _line+'\n'))
    #     except AttributeError:
    #         for dp in ready:
    #             print(_formatter.format(_line, dp.name, dp, dp.columns, _line))
    # @staticmethod
    # def reader_writer(meter, dater=None, **kwargs) -> Any:
    #     """  If a metric has been previously saved load save, else request metric """
    #     _save_dir: str = 'PSEUDO_BASE'
    #     _metric = f"{'_'.join(meter.split('/')).upper()}"
    #     # Mongo_Document_Format -> {_metric: dater.json()}
    #     if dater:
    #         logging.debug(f"Response: {dater}")
    #         # with open(file=f'{_save_dir}/{_metric}.json', mode='w') as filer:
    #         #     json.dump(dater.json(), filer)
    #     else:
    #         with open(file=f'{_save_dir}/{_metric}.json', mode='r') as filer:
    #             return json.loads(filer.readline())

    # def mongo_writer(self, index, endpoint, kwargs):
    #     with self._mongo_locks:
    #         dox = self.glass_quest(index=index, endpoint=endpoint, **kwargs)
    #         self.mongo_insert_one(one_dump=dox, col_name=f"{dox[2]['a'].upper()}_{dox[2]['i']}")

    def mongo_writer(self, index, endpoint, kwargs):
        with self._mongo_locks:
            dox = self.glass_quest(index=index, endpoint=endpoint, **kwargs)
            self.mongo_insert_one(one_dump=dox, col_name=f"{dox[2]['a'].upper()}_{dox[2]['i']}")

    def _magic_metrics(self, queries: List[Tuple[str, str, Dict[str, Any]]]):
        """ U.I. Layer, pass Tuple['idx', 'endpoint', Dict:[str(param), Any]] """
        for idx, ends, kwargs in queries:
            _writer = Thread(name='_MON_CLIENT_', target=self.mongo_writer, args=(idx, ends, kwargs))
            _writer.start()
            # try:
            #     # TODO Query database for stored metric before requesting from API
            #     # raise Exception('RECORD_NOT_FOUND_')
            # except Exception as e:
            #     # TODO Determine which exception will raised
            #     # logging.info(f'<bypass_triggered> : <{e}>')
            #     # _writer = Thread(name='_MON_CLIENT_', target=self.mongo_writer, args=(idx, ends, kwargs))
            #     # _writer.start()
        with self._mongo_locks:
            logging.warning('>>> _MONGO_LOCK_TERMINATED')
            self._results_ready.set()

    def magic_metrics(self, big_query: List[tuple]):
        _root_thread = Thread(name='_ROOT_THREAD', target=self._magic_metrics, args=(big_query,))
        _root_thread.start()
        self._results_ready.wait(timeout=5)
        _root_thread.join()
        self.kill_client()


def push_mongo_metrics(mons):
    _rapid_test = [
        ('market', 'marketcap_realized_usd', {'a': 'BTC'}),
        ('market', 'price_drawdown_relative', {'a': 'BTC'}),
        ('market', 'marketcap_usd', {'a': "BTC"}),
        ('market', 'mvrv_z_score', {'a': "BTC"}),
        ('market', 'price_usd_ohlc', {'a': "BTC"}),
        ('market', 'price_realized_usd', {'a': "BTC"}),
        ('supply', 'active_more_1y_percent', {'a': 'BTC'}),
        ('supply', 'current', {'a': 'BTC'}),
        ('blockchain', 'block_height', {'a': 'BTC'}),
        ('blockchain', 'block_height', {'a': 'BTC'}),
        ('indicators', 'stock_to_flow_ratio', {'a': 'BTC'}),
        ('indicators', 'hash_ribbon', {'a': 'BTC'}),
        ('indicators', 'difficulty_ribbon', {'a': 'BTC'}),
        ('indicators', 'realized_profit', {'a': 'BTC'}),
        ('indicators', 'realized_loss', {'a': 'BTC'}),
        ('indicators', 'reserve_risk', {'a': 'BTC'}),
        ('transactions', 'transfers_from_exchanges_count', {'a': 'BTC'}),
        ('transactions', 'transfers_to_exchanges_count', {'a': 'BTC'})
    ]
    mons.magic_metrics(_rapid_test)


def endpoints(glassed):
    foo_bar = glassed.get_endpoints()
    glassed.mongo_insert_many(foo_bar, col_name='GlassnodeEndpoints')


if __name__ == '__main__':
    # _PAT, _POINT, _PARA = 'market', 'price_usd_close', {'a': 'BTC'}
    # _PAT, _POINT, _PARA = 'indicators', 'hash_ribbon', {'a': 'BTC'}
    # NOTED = GlassClient()
    # TESTER = NOTED.glass_quest(index=_PAT, endpoint=_POINT, **_PARA)
    # LongHandler().mongo_encoder(TESTER)
    # quick_flush()
    glassed = Glassnodes()
    # endpoints(glassed)
    push_mongo_metrics(glassed)

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

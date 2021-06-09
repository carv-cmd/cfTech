# from functools import reduce
import os
import time
from datetime import datetime
from threading import Event, Lock
from queue import LifoQueue, Queue
from _queue import Empty

import ciso8601
from requests import Request, Session
from dotenv import load_dotenv, find_dotenv

from MongoDatabase.Mongos import Any, Optional, Dict, Tuple, List
from MongoDatabase.Mongos import logging, Thread, RLock
from MongoDatabase.Mongos import MongoBroker

load_dotenv(find_dotenv())

__all__ = [
    'Glassnodes',
    'LongHandler',
    'ciso8601',
    'datetime',
    'logging',
    'Thread',
    'Event',
    'Queue',
    'Optional',
    'Tuple',
    'Dict',
    'List',
    'Any'
]


class LongHandler:
    _Tm, _Tp, _Td = '_metrics', '_parameters', '_data'
    _DIVS, _LK, _MODIFY = '_divMask', '_divKeys', '_divModified'
    _OVERFLOW = 9223372036854774783
    _MASK = 4294967296

    @staticmethod
    def ciso_handler(ts: Any = None):
        """ _UTC_OFFSET = divmod(divmod(time.localtime().tm_gmtoff, 60)[0], 60)[0] """
        try:
            return ciso8601.parse_datetime(ts).timestamp()
        except ValueError:
            return datetime.utcfromtimestamp(ts).timestamp()
        except TypeError:
            return ts

    @staticmethod
    def _fallback_encoder(_long_keys, _latter_ki, _decoded,
                          _mask=_MASK, _d=_DIVS, _k=_LK, _m=_MODIFY) -> Dict:
        """
        :param _long_keys: keys flagged for overflow values
        :param _latter_ki: from -> {'v': Var[str, int, float], 'o': Dict(Any)}
        :param _decoded: JSON document flagged(int > MongoDB.8byte.limit)
        :param _mask: class_attr: see default
        :param _d: class_attr: see default
        :param _k: class_attr: see default
        :param _m: class_attr: see default

        :return: {_d: _mask, _k: _long_keys, _m: _decoded}
        """
        _start = datetime.now()
        for _item in _decoded:
            _item['t'] = ciso8601.parse_rfc3339(_item['t'])
            try:
                for failed in _long_keys:
                    _item[_latter_ki][failed] = divmod(_item[_latter_ki][failed], _mask)
            except TypeError:
                _item[_latter_ki] = divmod(_item[_latter_ki], _mask)
        logging.info(f'-> ENCODING.TIME(<{(datetime.now() - _start).total_seconds()}>) -> {_long_keys}\n')
        return {_d: _mask, _k: _long_keys, _m: _decoded}

    @staticmethod
    def _fallback_decoder(_encoded, _latter_ki, _mask, _long_ki) -> Dict:
        # _item['t'] = ciso8601.parse_rfc3339(_item['t'])
        _start = datetime.now()
        for _item in _encoded:
            try:
                for _mod_key in _long_ki:
                    _div_n1, _div_n2 = _item[_latter_ki][_mod_key]
                    _item[_latter_ki][_mod_key] = (_div_n1 * _mask) + _div_n2
            except KeyError:
                _div_s1, _div_s2 = _item[_latter_ki]
                _item[_latter_ki] = (_div_s1 * _mask) + _div_s2
        logging.info(f'-> DECODING.TIME(<{(datetime.now() - _start).total_seconds()}>) -> {_long_ki}\n')
        return _encoded

    def fallback_encoder(self, _json_decoded, _max_int64=_OVERFLOW, scan_skip=1000) -> Dict:
        """
        Moderate wizardry, as mongoOverFlow errors are interesting to handle.
        Scans for overflow conditions, if none return basic local format.
        If conditional; use divmod w/ class.attr mask saved in _data dictionary if ever needed.
        Consider long term growth of int > max_int64; set mask accordingly to avoid future reformatting.
        Current _MASK value is ideal for most conditions; stability is not guaranteed if changed.

        :param _json_decoded: Raw json response format from GlassnodeAPI
        :param _max_int64: Safe max integer size to store in MongoDB
        :param scan_skip: interval of in-range-skip

        :return: {_metrics: dict, _parameters: dict, _process: encoded_response}
        """
        _process = _json_decoded[0].json()
        _super_key = ('v' if 'v' in _process[0] else 'o')
        try:
            _unsafe = [[k for k, v in _process[ix][_super_key].items() if v > _max_int64]
                       for ix in range(0, len(_process), scan_skip)].pop()
        except AttributeError:
            _unsafe = [[_process[ix][_super_key] for ix in range(0, len(_process), scan_skip)
                        if _process[ix][_super_key] > _max_int64]].pop()
        if _unsafe:
            _process = self._fallback_encoder(_long_keys=_unsafe, _latter_ki=_super_key, _decoded=_process)
        return {self._Tm: _json_decoded[1], self._Tp: _json_decoded[2], self._Td: _process}

    def fallback_decoder(self, _json_encoded, _d=_DIVS, _k=_LK, _m=_MODIFY) -> Dict:
        """
        Decodes divmod.hakd datasets. See encoder for reasoning why.

        :param _json_encoded: dict: local_encoding_JSON
        :param _d: class_attr: default('_divMask', divmod.divisor)
        :param _k: class_attr: default('_divKeys', overFlow.keys)
        :param _m: class_attr: default('_divModified', modified.data)

        :return: Dict[(str: metric), (dict: parameters), (dict: data)]
        """
        try:
            _encoded = _json_encoded[self._Td]
            _decoded = self._fallback_decoder(
                _encoded=_encoded[_m],
                _latter_ki=('v' if 'v' in _encoded[_m][0] else 'o'),
                _mask=_encoded[_d],
                _long_ki=_encoded[_k]
            )
        except TypeError:
            _decoded = _json_encoded
        return _decoded


class _GlassBroker(LongHandler, MongoBroker):
    # Create .env file, save api_key under GLASSNODE, import with dotenv module
    _API_KEY = os.getenv('GLASSNODE')

    # If root paths are updated by vendor change class variables below
    _GLASSNODE = "https://api.glassnode.com/v1/metrics"
    _HELPER = "https://api.glassnode.com/v2/metrics/endpoints"

    __slots__ = ('_session',)

    def __init__(self, start=True, ip='127.0.0.1:27017', db='Glassnodes'):
        super(_GlassBroker, self).__init__(start=start, client_ip=ip, db_name=db)
        self._session = Session()

    def _request(self, req_method: str, target: str, params: Optional[Dict[str, Any]] = None) -> Tuple:
        """
        <GET> only method currently implemented. Handles all request.methods, I think?

        :param req_method: HTTP request method. Default(<GET>)
        :param target: Full api request endpoint. **constructed by caller
        :param params: Asset('a') required, all others autogenerated when needed

        :return: dict(key=request_endpoint, value=[asset_name, response.json])
        """
        logging.info(f'* <REQUEST[ <{datetime.now()}> ? <{target}>]>')
        response = self._session.send(Request(
            method=req_method, url=target, params={**params, **{'api_key': self._API_KEY}}).prepare())
        response.close()
        (reason, stat_code, url) = (response.reason, response.status_code, response.url)
        resp_str = f'* <RESPONSE[<{datetime.now()}>:({reason}:{stat_code})]>'
        assert stat_code != 429, f"{resp_str}\n?{url}"
        assert stat_code != 403, f"{resp_str}\n?{url}"
        assert stat_code == 200, f"{resp_str}"
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
        assert 'a' in kwargs, "AbsMinParams=('asset')"
        return self._request('GET', target=f'{self._GLASSNODE}/{index}/{endpoint}', params=kwargs)


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
        'index', 'endpoint'
    )
    _PARAMS = __slots__[0: 8]

    def __init__(self,
                 index: str = None, endpoint: str = None, a: str = None,
                 s: str = None, u: str = None, i: str = '24h', f: str = 'JSON',
                 c: str = None, e: str = None, timestamp_format: str = 'humanized'):
        """

        * EXAMPLE START/UNTIL TIMESTAMPS BELOW:
        * All timestamps: [<defined as UTC> & <refer to interval start>]

        Monthly resolution: -> (May:2019)
         * <2019-05-01 00:00> TO <2019-05-31 23:59>
        Weekly resolution: -> (Week:20)
         * <2019-05-13 00:00> TO <2019-05-19 23:59>
        Daily resolution: -> (Day:5)
         * <2019-05-13 00:00> TO <2019-05-13 23:59>
        Hourly resolution:
         * <2019-05-13 10:00> TO <2019-05-13 10:59>
        10 Min resolution:
         * <2019-05-13 10:20> TO <2019-05-13 10:29>

        * "API_KEY": str = autofill(SEE: _GlassBroker.class.attrs)

        :param index: str = ex.'indicators'
        :param endpoint: str = ex.'hash_ribbon'
        :param a: str = asset('BTC')
        :param s: str = ISO-8601: [YYYY-MM-DD HH:MM]
        :param u: str = ISO-8601: [YYYY-MM-DD HH:MM]
        :param i: str = freq_interval(['1h', '24h', '10m', '1w', '1month'])
        :param f: str = format(['JSON', 'CSV'])
        :param c: str = currency(['NATIVE', 'USD'])
        :param e: str = exchange(['aggregated','binance','bittrex','coinex','gate.io','huobi','poloniex'])
        :param timestamp_format: str = [use('UNIX'), 'humanized(RFC-3339)']

        """
        super(_GlassClient, self).__init__()
        self.index = index
        self.endpoint = endpoint
        self.params = dict(filter(lambda fk: fk[0] in self._PARAMS, locals().copy().items()))
        self.set_attributes(kwargs=self.params)

    def set_attributes(self, **kwargs):
        """ Class attribute setter. """
        try:
            _params = {**getattr(self, 'params'), **kwargs['kwargs']}
            for su in ['s', 'u']:
                if _params[su] is not None:
                    _params[su] = int(self.ciso_handler(_params[su]))
            setattr(self, 'params', _params)
        except KeyError:
            for k, v in kwargs.items():
                setattr(self, k, v)

    def glass_quest(self, index: str = None, endpoint: str = None, **kwargs):
        """
        Class attribute setter/getter method, stores request parameters.
        Make repetitive requests w/ only single new attribute passed in each method call.
        Default start/until parameters are None, or equivalent to 'total_historical'.
        Due to the above conditions, response size of smaller intervals can be exceedingly large.
        Account for this by iteratively stepping dates through start/until period.

        :param index: https//api.glassnode.com/v1/metrics/<<index>>
        :param endpoint: api.glassnode.com/v1/metrics/index/<<endpoint>>
        :param kwargs: dict(RequestParameters) -> see _init_.docstring
        :return: Tuple[Response, 'index_endpoint', params]
        """
        qc = locals().copy()
        if index and endpoint is not None:
            self.set_attributes(index=qc['index'], endpoint=qc['endpoint'])
        elif endpoint is not None:
            self.set_attributes(endpoint=qc['endpoint'])
        if any(qc['kwargs']):
            self.set_attributes(kwargs=qc['kwargs'])
        assert self.index and self.endpoint and self.params['a'] is not None, "REQUIRED ATTRIBUTES !EXIST"
        return self.get_metrics(
            getattr(self, 'index'), getattr(self, 'endpoint'),
            **dict(filter(lambda fx: fx[1] is not None, getattr(self, 'params').items()))
        )


class Glassnodes(_GlassClient, LongHandler):

    __slots__ = ('_mon_writes', '_response_recv', '_mon_locker', '_queued', 'external_flag', 'loaded')

    def __init__(self):
        super(Glassnodes, self).__init__()
        self._mon_writes = Thread(name='Mongo_WRITES', target=self._mongo_response_loader)
        self._response_recv = Event()
        self._mon_locker = RLock()
        self._queued = LifoQueue()
        self.external_flag = Event()
        self.loaded = []

    def _mongo_response_loader(self):
        """
        :return:
        """
        while True:
            # self.mongo_replace_one(one_dox=_dox, col_name=f"{_dox[2]['a']}_{_dox[2]['i']}".upper())
            try:
                self._response_recv.wait(timeout=8)
                _dox = self._queued.get(timeout=0.01)
                self.mongo_insert_one(one_dox=_dox, col_name=f"{self.params['a']}_{self.params['i']}".upper())
                self.loaded.append(self.mongo_query({'_metrics': {'$eq': _dox[1]}}, projection={'id': False}))
                self._queued.task_done()
            except Empty:
                self._queued.all_tasks_done = True
                break

    def _requester(self, queries: Tuple[str, str, Dict[str, Any]]):
        """
        If doc not found in db.collection.instance, request parameters are passed to this method.
        Response is placed in queue, _mon_writes thread started to execute database loading.

        :param queries: QueryTuple[str:index, str:endpoint, **Dict[str, Any]:request_params]
        :return: None, method is queue arbiter
        """
        with self._mon_locker:
            try:
                _passing = queries[2]
            except IndexError:
                _passing = self.params
            finally:
                self._queued.put(self.glass_quest(index=queries[0], endpoint=queries[1], **_passing))
                self._response_recv.set()
                self._response_recv.clear()

    def _mongo_reader(self, q_filter: Tuple[str, str, Dict[str, Any]]):
        """
        :param q_filter:
        :return:
        """
        try:
            self.set_attributes(kwargs=q_filter[2])
        except IndexError:
            pass
        self.set_collection(collection_name=f"{self.params['a']}_{self.params['i']}".upper())
        return self.mongo_query(
            user_defined={'_metrics': {'$eq': f'{q_filter[0]}_{q_filter[1]}'.upper()}},
            projection={'_id': False}
        )

    def magic_metrics(self, big_query: List[Tuple[str, str, Dict[str, Any]]]) -> None:
        """
        BatchQueryMethod -> Glassnode metrics.

        :param big_query: List[Tuple[str:index, str:endpoint, Dict[str, Any]]
        :return: None
        """
        self._mon_writes.start()
        for query in big_query:
            try:
                self.loaded.append(self._mongo_reader(query))
            except IndexError:
                _requester = Thread(name="REQUESTING", target=self._requester, args=(query, ), daemon=True)
                _requester.start()
            except AssertionError as e:
                # time.sleep(61)
                # print(e)
                pass
        with self._mon_locker:
            self._queued.join()
            self._response_recv.set()
            self.kill_client()
            self.external_flag.set()

    def get_loaded(self):
        return self.loaded


if __name__ == '__main__':
    from pprint import pprint
    tup = [
        ('market', 'price_usd_close', {'a': 'BTC', 's': '2020-05-01', 'i': '24h'}),
        ('indicators', 'difficulty_ribbon'),
        # ('market', 'price_usd_ohlc'),
        # ('indicators', 'hash_ribbon')
    ]
    fached = Glassnodes()
    fached.magic_metrics(tup)
    fached.external_flag.wait()
    # pprint(fached.get_loaded(), width=120)

    # fached.mongo_drop_collection(drop_col='BTC_24H', check=True)


else:
    logging.debug(f'>>> Initialized {__name__} @ <{datetime.now()}>\n')

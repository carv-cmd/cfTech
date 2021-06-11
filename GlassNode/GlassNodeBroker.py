# from gevent import monkey; monkey.patch_all()
# from gevent import monkey; monkey.patch_queue(), monkey.patch_thread()
# import tracemalloc

import os
import json
import time
from datetime import datetime

import asyncio
import aiohttp
import ciso8601
from dotenv import load_dotenv, find_dotenv
from requests import get

from MongoDatabase.Mongos import Any, Optional, Dict, Tuple, List
from MongoDatabase.Mongos import logging
from MongoDatabase.Mongos import MongoBroker

load_dotenv(find_dotenv())


__all__ = [
    'LongHandler',
    'ciso8601',
    'datetime',
    'logging',
    'Optional',
    'Tuple',
    'Dict',
    'List',
    'Any'
]


class LongHandler:
    _Tm, _Tp, _Td = 'Metrics', 'Parameters', 'Datas'
    _DIVS, _LK, _MODIFY = 'DivMask', 'DivKeys', 'DivModified'
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
    def _time_encoder(_decoded, _mask=_MASK, _d=_DIVS, _k=_LK, _m=_MODIFY):
        for _ts in _decoded:
            _ts['t'] = ciso8601.parse_rfc3339(_ts['t'])
        return _decoded


    @staticmethod
    def _fallback_encoder(_long_ki, _latter_ki, _decoded, _mask=_MASK, _d=_DIVS, _k=_LK, _m=_MODIFY) -> Dict:
        """
        Work around for MongoDB 8-byte int limit that retains int accuracy at its full resolution

        :param _long_ki: keys flagged for overflow values
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
                for failed in _long_ki:
                    _item[_latter_ki][failed] = divmod(_item[_latter_ki][failed], _mask)
            except TypeError:
                _item[_latter_ki] = divmod(_item[_latter_ki], _mask)
        logging.info(f'-> ENCODING.TIME(<{(datetime.now() - _start).total_seconds()}>) -> {_long_ki}\n')
        return {_d: _mask, _k: _long_ki, _m: _decoded}

    @staticmethod
    def _fallback_decoder(_long_ki, _latter_ki, _encoded, _mask) -> Dict:
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

    def fallback_encoder(self, _json_decoded, _max_int64=_OVERFLOW) -> Dict:
        """
        Scans len(1/10) for overflow conditions, if none return basic local formatting.
        If conditional; use divmod w/ class.attr mask saved in _data dictionary if ever needed.
        Consider long term growth of int > max_int64; set mask accordingly to avoid future reformatting.
        Current _MASK value is ideal for most conditions; stability is not guaranteed if changed.

        :param _json_decoded: Raw json response format from GlassnodeAPI
        :param _max_int64: Safe max integer size to store in MongoDB
        :return: {_metrics: dict, _parameters: dict, _process: encoded_response}
        """
        _process = json.loads(_json_decoded[0])
        _super_key = ('v' if 'v' in _process[0] else 'o')
        _scan_skip = len(_process) // 10
        try:
            _unsafe = [[k for k, v in _process[ix][_super_key].items() if v > _max_int64]
                       for ix in range(0, len(_process), _scan_skip)].pop()
        except AttributeError:
            _unsafe = [[_process[ix][_super_key] for ix in range(0, len(_process), _scan_skip)
                        if _process[ix][_super_key] > _max_int64]].pop()
        if not _unsafe:
            for xyz in _process:
                xyz['t'] = ciso8601.parse_rfc3339(xyz['t'])
        else:
            _process = self._fallback_encoder(_long_ki=_unsafe, _latter_ki=_super_key, _decoded=_process)
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
                _long_ki=_encoded[_k],
                _latter_ki=('v' if 'v' in _encoded[_m][0] else 'o'),
                _encoded=_encoded[_m],
                _mask=_encoded[_d]
            )
        except Exception as e:
            print(e)
            _decoded = _json_encoded
        return _decoded


class GlassRoots(LongHandler, MongoBroker):
    _API_KEY = {'api_key': os.getenv('GLASSNODE')}

    # If root paths are updated by vendor change class variables below
    _NODE = "https://api.glassnode.com/v1/metrics"
    _HELPER = "https://api.glassnode.com/v2/metrics/endpoints"

    # Endpoint fast/lazy requests-projection-filter
    _ID_IGNORE = {'_id': False}

    def __init__(self, start=True, ip='127.0.0.1:27017', db='Glassnodes'):
        super(GlassRoots, self).__init__(start=start, client_ip=ip, db_name=db)

    def _get_endpoints(self, specified: Dict = None, projector: Dict = None, updates: bool = None) -> List:
        """
        :param specified: ex. { $and: [{"tier": 1}, {"assets.symbol": {"$eq": 'BTC'}}]}
        :param updates: if true, db.GlassPoints.drop, db.GlassPoints.insert(request); else db.loader
        :return: List[Dicts[endpoint_data]]
        """
        if updates:
            self.mongo_drop_collection('GlassPoints', check=updates)
            with get(self._HELPER, params=self._API_KEY) as quick_help:
                _refreshed = quick_help.json()
            for eps in _refreshed:
                eps['path'] = eps['path'].split('/')[-2:]
            self.mongo_insert_many(big_dump=_refreshed, col_name='GlassPoints')
        try:
            self.set_collection(collection_name='GlassPoints')
            _finder = list(self.working_col.find(specified, projection={**self._ID_IGNORE, **projector}))
        except Exception as e:
            logging.warning(f'* Raised: {e}')
            _finder = list(self.working_col.find(projection=self._ID_IGNORE))
        return _finder

    def get_endpoints(self, tier: str, asset: str, currencies: str, resolutions: str,
                      formatting: str, update: bool, query_proj: dict = None) -> List:
        _EPP = (
            {'tier': False, 'assets': False, 'currencies': False, 'resolutions': False, 'formats': False}
            if query_proj is None else query_proj
        )

        _endpoint_query = {
            "$and": [
                {"tier": {"$in": [int(n) for n in tier.split('/')]}},
                {"assets.symbol": {"$in": asset.upper().split('/')}},
                {'currencies': {"$in": currencies.upper().split('/')}},
                {"resolutions": {"$in": resolutions.split('/')}},
                {"formats": {"$in": formatting.upper().split('/')}}
            ]
        }
        _projected = self._get_endpoints(
            specified=_endpoint_query,
            projector={**self._ID_IGNORE, **_EPP},
            updates=update
        )
        return [elem['path'] for elem in _projected]

    def quick_query(
        self,
        tier: str = '1/2/3',
        asset: str = 'BTC',
        currencies: str = 'NATIVE/USD',
        resolutions: str = "10m/1h/24h/1w/1month",
        formatting: str = 'JSON/CSV',
        update: bool = None,
        specify: list = None,
        prep: dict = None
    ):
        """
        Query Glassnode indices/endpoints for available options.
        Any grouped function parameters should be separated by '/' symbol for safe split.

        :param tier: str = '1/2/3'
        :param asset: str = 'BTC/ETH'
        :param currencies: str = 'NATIVE/USD'
        :param resolutions: str = '10m/1h/24h/1w/1month'
        :param formatting: str = 'JSON/CSV'
        :param update: bool = 'True' to update stored endpoints
        :param specify: list = available glassnode indices to return
        :param : dict = pass to prep glass_quest signature in one call (applies-like-params)
        :return: Given query filter returns all endpoints matching either semi/fully prepped
        """
        _locals_copy = locals().copy().items()
        _ignore_locals = ['self', 'specify', 'prep']
        _res = self.get_endpoints(**dict(filter(lambda x: x[0] not in _ignore_locals, _locals_copy)))
        if specify is not None:
            _res = list(filter(lambda x: x[0] in specify, _res))
        if prep is not None:
            _res = [(*mx, prep) for mx in _res]
        return _res


class GlassnodeAPI(GlassRoots):

    __slots__ = ('_sesh', )

    def __init__(self):
        super(GlassnodeAPI, self).__init__()
        self._sesh = aiohttp.ClientSession

    def batch_metrics(self, _prepped):
        async def _aio_pooler(target, params):
            async with self._sesh() as session:
                async with session.get(target, params=params) as response:
                    return await response.text()
        _ev_loop = asyncio.get_event_loop()
        _req_params = {**_prepped[0][2], **self._API_KEY}
        _req_coroutines = [_aio_pooler(f'{self._NODE}/{bx[0]}/{bx[1]}', _req_params) for bx in _prepped]
        return zip(_ev_loop.run_until_complete(asyncio.gather(*_req_coroutines)), _prepped)

    def mongo_reqs_writes(self, response_set):
        """
        :return:
        """
        for _dox in self.batch_metrics(response_set):
            _response_tuple = (_dox[0], f"{_dox[1][0]}_{_dox[1][1]}".upper(), _dox[1][2])
            _insert_collection = f"{_dox[1][2]['a']}_{_dox[1][2]['i']}"
            self.mongo_insert_one(one_dox=_response_tuple, col_name=_insert_collection)
            # self.loaded.append(self.mongo_query({self._Tm: {'$eq': _dox[1]}}, projection={'id': False}))
            # jason = _dox.text()
            # print(type(jason[0]))
            # print(jason)
            # jason = json.loads(jason)
            # self.mongo_insert_one(one_dox=_dox, col_name=f"{self.params['a']}_{self.params['i']}".upper())

    def mongo_loads_reads(self):
        pass


def set_params(a=None, s=None, u=None, i=None, f=None, c=None, e=None, timestamp_format=None):
    """
    * EXAMPLE START/UNTIL TIMESTAMPS BELOW:
    * All timestamps: [<defined as <UTC> & <refer to interval start>]
    Monthly resolution: -> (May:2019)
     * <2019-05-01 00:00> THRU <2019-05-31 23:59>
    Weekly resolution: -> (Week:20)
     * <2019-05-13 00:00> THRU <2019-05-19 23:59>
    Daily resolution: -> (Day:5)
     * <2019-05-13 00:00> THRU <2019-05-13 23:59>
    Hourly resolution:
     * <2019-05-13 10:00> THRU <2019-05-13 10:59>
    10 Min resolution:
     * <2019-05-13 10:20> THRU <2019-05-13 10:29>

    * "API_KEY": str = autofill(SEE: _GlassBroker.class.attrs)

    :param a: str = asset('BTC')
    :param s: str = ISO-8601: [YYYY-MM-DD HH:MM]
    :param u: str = ISO-8601: [YYYY-MM-DD HH:MM]
    :param i: str = freq_interval(['1h', '24h', '10m', '1w', '1month'])
    :param f: str = format(['JSON', 'CSV'])
    :param c: str = currency(['NATIVE', 'USD'])
    :param e: str = exchange(['aggregated','binance','bittrex','coinex','gate.io','huobi','poloniex'])
    :param timestamp_format: str = ['*humanized(RFC-3339)*', 'UNIX']
    """
    _local_copy = locals().copy().items()
    _build = dict(filter(lambda bx: bx[1] is not None, _local_copy))
    for timestamps in [ts for ts in _build if ts in ['s', 'u']]:
        _build[timestamps] = int(ciso8601.parse_datetime(_build[timestamps]).timestamp())
    return _build


if __name__ == '__main__':
    pass

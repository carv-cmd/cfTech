# from gevent import monkey; monkey.patch_all()
# from gevent import monkey; monkey.patch_queue(), monkey.patch_thread()
# from threading import Timer
import os

import time
from datetime import datetime
import asyncio
from aiohttp import ClientSession
import ciso8601
from requests import get
import tracemalloc
from dotenv import load_dotenv, find_dotenv

from bson.json_util import loads
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

tracemalloc.start()


class LongHandler:
    _MET, _PAR, _LAST, _DATA = 'Metric', 'Parameters', 'Updated', 'Data'
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
    def _just_time(_decoded):
        for xyz in _decoded:
            xyz['t'] = ciso8601.parse_rfc3339(xyz['t'])
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
        _params, _process = _json_decoded[1], _json_decoded[2]
        _super_key = ('v' if 'v' in _process[0] else 'o')
        _scan_skip = len(_process) // 10
        _fix = []
        for _index in range(0, len(_process), _scan_skip):
            try:
                _fix = [k for k, v in _process[_index][_super_key].items() if v > _max_int64]
            except AttributeError:
                if _process[_index][_super_key] > _max_int64:
                    _fix = _process[_index][_super_key]
                break
        if _fix:
            _process = self._fallback_encoder(_long_ki=_fix, _latter_ki=_super_key, _decoded=_process)
        else:
            for xyz in _process:
                xyz['t'] = ciso8601.parse_rfc3339(xyz['t'])
        return {
            self._MET: _json_decoded[0],
            self._PAR: {'IdxEndpt': _params[0], 'Signature': _params[1]},
            self._LAST: datetime.now(),
            self._DATA: _process
        }

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
            _encoded = _json_encoded[self._DATA]
            _decoded = self._fallback_decoder(
                _long_ki=_encoded[_k],
                _latter_ki=('v' if 'v' in _encoded[_m][0] else 'o'),
                _encoded=_encoded[_m],
                _mask=_encoded[_d]
            )
        except TypeError:
            _decoded = _json_encoded
        except Exception as e:
            raise e
        return _decoded


class _GlassPoints(LongHandler, MongoBroker):
    _API_KEY = {'api_key': os.getenv('GLASSNODE')}

    # If root paths are updated by vendor change class variables below
    _NODE = "https://api.glassnode.com/v1/metrics"
    _HELPER = "https://api.glassnode.com/v2/metrics/endpoints"

    def __init__(self, start=True, ip='127.0.0.1:27017', db='Glassnodes'):
        super(_GlassPoints, self).__init__(start=start, client_ip=ip, db_name=db)

    @staticmethod
    def set_params(a=None, s=None, u=None, i=None, f=None, c=None, e=None, timestamp_format=None):
        raise NotImplementedError()

    @staticmethod
    def _divide_requests(_gator):
        (_double_gator, _gator_length, _safe_gator) = (_gator.copy(), len(_gator), 25)
        _request_lim, _null = divmod(_gator_length, _safe_gator)
        _cut_gator = [[_gator.pop() for _r1 in range(_safe_gator)] for _ in range(_request_lim)]
        _cut_gator.append(_gator)
        return _cut_gator

    def _load_endpoints(self, spec: Dict = None, projector: Dict = None, updates: bool = None) -> List:
        """
        :param spec: ex. { $and: [{"tier": 1}, {"assets.symbol": {"$eq": 'BTC'}}]}
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
            _finder = list(self.working_col.find(spec, projection={**self._ID_IGNORE, **projector}))
        except Exception as e:
            logging.warning(f'* Raised: {e}')
            _finder = list(self.working_col.find(projection=self._ID_IGNORE))
        return _finder

    def load_endpoints(self, tier: str, asset: str, currencies: str, resolutions: str,
                       formats: str, update: bool, query_proj: dict = None) -> List:
        _endpoint_query = {
            "$and": [
                {"tier": {"$in": [int(n) for n in tier.split('/')]}},
                {"assets.symbol": {"$in": asset.upper().split('/')}},
                {'currencies': {"$in": currencies.upper().split('/')}},
                {"resolutions": {"$in": resolutions.split('/')}},
                {"formats": {"$in": formats.upper().split('/')}}
            ]
        }
        if query_proj is None:
            _project_all = ['tier', 'assets', 'currencies', 'resolutions', 'formats']
            query_proj = dict(map(lambda x: (x, False), _project_all))
        _projected = self._load_endpoints(
            spec=_endpoint_query,
            projector={**self._ID_IGNORE, **query_proj},
            updates=update
        )
        return [elem['path'] for elem in _projected]

    def quick_query(
        self,
        tier: str = '1/2/3',
        asset: str = 'BTC',
        currencies: str = 'NATIVE/USD',
        resolutions: str = "10m/1h/24h/1w/1month",
        formats: str = 'JSON/CSV',
        *,
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
        :param formats: str = 'JSON/CSV'
        :param update: bool = 'True' to update stored endpoints
        :param specify: list = available glassnode indices to return
        :param : dict = pass to prep glass_quest signature in one call (applies-like-params)
        :return: Given query filter returns all endpoints matching either semi/fully prepped
        """
        _locals_copy = locals().copy().items()
        _ignore_locals = ['self', 'specify', 'prep']
        _res = self.load_endpoints(**dict(filter(lambda x: x[0] not in _ignore_locals, _locals_copy)))
        if specify is not None:
            _res = list(filter(lambda x: x[0] in specify, _res))
        if prep is not None:
            prep = self.set_params(**prep)
            _res = [(*mx, prep) for mx in _res]
        if len(_res) > 25:
            logging.info(f'* len(Gators).quick_query() -> {len(_res)}')
            _res = self._divide_requests(_res)
        return _res


class GlassnodeAPI(_GlassPoints):
    # _ANNOYING = {'CONTENT-TYPE': 'application/json'}
    _PASSING = ['_id', 'Parameters', 'Updated', 'Data']
    __slots__ = ('_sesh', '_in_memory', '_process_raw', '_working_datasets', '_bad_requests')

    def __init__(self):
        super(GlassnodeAPI, self).__init__()
        self._sesh = ClientSession
        self._in_memory = []
        self._process_raw = []
        self._working_sets = []
        self._bad_requests = []

    def _batch_metrics(self, preps):
        async def _aio(target, params):
            async with self._sesh() as session:
                async with session.get(target, params=params) as resp:
                    _initial = f"(<{resp.status}:{resp.reason}>)"
                    logging.info(f"* Request{_initial}:?{target}")
                    if resp.status != 200:
                        resp = {'Response': dict(resp.headers), 'Status': _initial, 'URL': str(resp.url)}
                    else:
                        resp = await resp.text()
                    return resp
        _path, _parameters = self._NODE, {**preps[0][1], **self._API_KEY}
        _ev_loop = asyncio.get_event_loop()
        _coroutines = [_aio(f'{_path}/{_ep[0]}/{_ep[1]}', _parameters) for _ep, _dk in preps]
        return _ev_loop.run_until_complete(asyncio.gather(*_coroutines))

    def write_requests(self, _signed_ray, _collection: str = None):
        for _sign, _dox in list(_signed_ray):
            try:
                assert isinstance(_dox, str)
                _data_label = f"{'_'.join(_sign[0])}".upper()
                _one_dox = (_data_label, _sign, loads(_dox))
                self._process_raw.append(self.fallback_encoder(_one_dox))
            except AssertionError:
                _baddie = {'Signature': _sign[0], 'Params': _sign[1], 'StatusHeader': _dox}
                self._bad_requests.append(_baddie)
            _len_p, _len_r = len(self._process_raw), len(self._bad_requests)
            # logging.info(f'* len(Processed, !Request): ({_len_p}, {_len_r})')
        self.mongo_insert_many(self._process_raw)
        self.mongo_insert_many(self._bad_requests, col_name='BadRequests')

    def read_loader(self, formatted: List[Tuple[Any, Dict]]):
        self.set_collection(f"{formatted[0][2]['a']}_{formatted[0][2]['i']}".upper())
        _memory = self.working_col.find(projection={_proj: False for _proj in self._PASSING})
        _on_disk, _no_local = [k['Metric'] for k in list(_memory)], []
        for _fock in formatted:
            if '_'.join([_fock[0], _fock[1]]).upper() in _memory:
                self._in_memory.append(_fock)
            else:
                _no_local.append(_fock)  # TODO known.BadRequest.ignore()
        if any(_no_local):
            _req_signature = [((_eps[0], _eps[1]), _eps[2]) for _eps in _no_local]
            _document_array = self._batch_metrics(preps=_req_signature)
            self.write_requests(zip(_req_signature, _document_array))

    def glass_lines(self, specify: list = None, parameters: dict = None, updating: bool = False):
        _sleeper, _testing = 0, 1
        _sepr = ''.join(['-' for _ in range(80)])
        _hedgies = self.quick_query(update=updating, specify=specify, prep=parameters)
        # _hedgies = [_hedgies[0][:4]]
        pprint(_hedgies[0], width=160, sort_dicts=False)
        for _degenerates in _hedgies:
            time.sleep(_sleeper)
            self.read_loader(_degenerates)
            _sleeper = 65

    @staticmethod
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
            _build[timestamps] = int(ciso8601.parse_datetime(str(_build[timestamps])).timestamp())
        return _build


if __name__ == '__main__':
    from pprint import pprint
    _ape = GlassnodeAPI()
    _specific = ['market', 'indicators']
    _calling = {'a': 'BTC', 'i': '24h', 'f': 'JSON', 'timestamp_format': 'humanized'}
    _ape.glass_lines(specify=_specific, parameters=_calling)
    _ape.kill_client()

# pymongo.errors.BulkWriteError: batch op errors occurred,
#   full error: {
#     'writeErrors': [
#         {'index': 0,
#         'code': 11000,
#         'keyPattern': {'_id': 1},
#         'keyValue': {'_id': ObjectId('60c599560afdb307e963055c')},
#         'errmsg': "E11000 duplicate key error collection:
#             Glassnodes.BTC_24H index:
#               _id_ dup key: { _id: ObjectId('60c599560afdb307e963055c') }",

# pymongo.errors.BulkWriteError: batch op errors occurred,
#   full error: {
#   'writeErrors': [{
#       'index': 0,
#       'code': 11000,
#       'keyPattern': {'_id': 1},
#       'keyValue': {'_id': ObjectId('60c59df47eb19b055db73dc0')},
#       'errmsg': "E11000 duplicate key error collection:
#           Glassnodes.BTC_24H index:
#               _id_ dup key: { _id: ObjectId('60c59df47eb19b055db73dc0') }",
#                   'op': {'Metric': 'MARKET_PRICE_REALIZED_USD',


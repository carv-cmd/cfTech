# import bisect
# import asyncio
import logging
import time
from datetime import datetime
from collections import defaultdict
from typing import Any, Dict, Tuple, List
from ciso8601 import parse_datetime, parse_rfc3339
from bson.json_util import loads as util_loads

from MongoDatabase.Mongos import MongoBroker, MongoServerStats
from EASYapi.RESTapi import AioHttpREST
from LoggerTools.logConfigurator import configure_logging


__all__ = ['GlassAIO', 'MongoServerStats']

logger = logging.getLogger('EASYapi.RESTapi')

configure_logging(mon_lvl='INFO', aio_lvl='INFO')


class MongoHandler(MongoBroker):

    _DOX_SCHEMA = ('Metric', 'Updated', 'Parameters', 'Data')
    _TUPLE_SIG = ('TuplePath', 'Signature')
    _DIV_KEYS = ('DivMask', 'DivKeys', 'DivModified')
    _OVERFLOW = 9223372036854774783
    _MASK = 4294967296
    _ENCODE_SCHEMA = [_MASK, *_DIV_KEYS]

    def __init__(self, start=True, ip='127.0.0.1:27017', db='Glassnodes'):
        super(MongoHandler, self).__init__(start=start, mon_ip=ip, db_name=db)

    @staticmethod
    def iso_local_utc() -> datetime:
        """
        Local update timestamp in <UTC> context.
        LocalOffset == -4hours.
        Update_Orchestrator_Ref_Point: document['Updated'].utc_offset(-4hours)
        :return: datetime.datetime local obj in <UTC> context
        """
        # TODO UTC-4 offset conversion codec
        return datetime.utcnow().replace(second=0, microsecond=0)

    @staticmethod
    def ciso_handler(ts: Any = None):
        """ _UTC_OFFSET = divmod(divmod(time.localtime().tm_gmtoff, 60)[0], 60)[0] """
        try:
            return parse_datetime(ts).timestamp()

        except ValueError:
            return datetime.utcfromtimestamp(ts).timestamp()

        except TypeError:
            return ts

    @staticmethod
    def _fallback_encoder(_longs, _latters, _decoded, _mask, _d, _k, _m) -> Dict:
        """
        Work around for MongoDB 8-byte int limit that retains int accuracy at its full resolution

        :param _longs: keys flagged for overflow values
        :param _latters: from -> {'v': Var[str, int, float], 'o': Dict(Any)}
        :param _decoded: JSON document flagged(int > MongoDB.8byte.limit)
        :param _mask: class_attr: see default
        :param _d: class_attr: see default
        :param _k: class_attr: see default
        :param _m: class_attr: see default

        :return: {_d: _mask, _k: _long_keys, _m: _decoded}
        """
        for _item in _decoded:

            _item['t'] = parse_rfc3339(_item['t'])

            try:
                for failed in _longs:
                    _item[_latters][failed] = divmod(_item[_latters][failed], _mask)
            except TypeError:
                _item[_latters] = divmod(_item[_latters], _mask)

        return {_d: _mask, _k: _longs, _m: _decoded}

    def fallback_encoder(self, _updated_at, _decoded, _max_int64=_OVERFLOW) -> Dict:
        """
        Scans len(1/10) for overflow conditions, if none return basic local formatting.
        If conditional; use divmod w/ class.attr mask saved in _data dictionary if ever needed.
        Consider long term growth of int > max_int64; set mask accordingly to avoid future reformatting.
        Current _MASK value is ideal for most conditions; stability is not guaranteed if changed.

        :param _decoded: Raw json response format from GlassMongoAPI
        :param _max_int64: Safe max integer size to store in MongoDB
        :return: {_metrics: dict, _parameters: dict, _process: encoded_response}
        """
        _start = time.monotonic()
        _process = util_loads(_decoded[2].tobytes())
        (_metric, _param) = (_decoded[0], _decoded[1])
        _set_len, _nest_key = (len(_process), ('v' if 'v' in _process[0] else 'o'))
        _overflow = []

        for _index in range(0, _set_len, _set_len // 10):
            try:
                _overflow = [k for k, v in _process[_index][_nest_key].items() if v > _max_int64]
            except AttributeError:
                if _process[_index][_nest_key] > _max_int64:
                    _overflow = _process[_index][_nest_key]
                break

        if not _overflow:
            for xyz in _process:
                xyz['t'] = parse_rfc3339(xyz['t'])
        else:
            _encode_tuple = (_overflow, _nest_key, _process, *self._ENCODE_SCHEMA)
            _process = self._fallback_encoder(*_encode_tuple)

        _parameters = dict(zip(self._TUPLE_SIG, [*_param]))
        logger.info(f"-> ENCODING.TIME(<{(time.monotonic() - _start)}>) -> {_metric}")
        return dict(zip(self._DOX_SCHEMA, [_metric, _updated_at, _parameters, _process]))


class GlassHandler(AioHttpREST, MongoHandler):

    _HELPERS = ('zxGlassPoints', 'zxBadRequests')
    _ROOT_METRICS = "https://api.glassnode.com/v2"  # -> metricsEndpoint
    _DENIED = ['Signature', 'Params', 'StatusHeader']  # -> write_requester.method
    _GET_DOX = ('Signature', 'Parameters', 'TuplePath')  # -> dox_on_disk/
    _API_KEY = 'GLASSNODE'

    def __init__(self):
        super(GlassHandler, self).__init__()
        self._in_memory = defaultdict(list)
        self._process_raw = []
        self._bad_requests = []
        self._total_rows_counter = 0

    def _endpt_updates(self, _updates: bool):
        """ Drop current endpoint collection and reload updated listings."""
        self.mongo_drop_collection(self._HELPERS[0], check=_updates)
        self.api_key = self._API_KEY
        _base_pts = [("metrics", "endpoints")]
        self.pooled_aio(endpoints=_base_pts, parameters={}, base_url=self._ROOT_METRICS)

    def endpt_query(self, filters):
        try:
            _gen_filter = {"$and": []}
            for _key, _val in filters:
                _val = _val.upper().split('/')

                if _key in ['tier']:
                    _val = [int(n) for n in _val]
                elif _key in ['assets']:
                    _key = 'assets.symbol'
                elif _key in ['resolutions']:
                    _val = [_v.lower() for _v in _val]

                _gen_filter["$and"].append({_key: {"$in": _val}})

        except TypeError:
            _gen_filter = filters

        _projection = {'path': True}
        _cox = self.mongo_query(self._HELPERS[0], _gen_filter, _projection)
        return [idx['path'] for idx in _cox]

    def load_endpoints(self, update=None, specify=None, filters=None) -> List:
        """

        :param update: Update endpoint collection. If true execute before main get request.
        :param specify:
        :param filters:
        :return:
        """
        if update:
            self._endpt_updates(update)

        _queried = self.endpt_query(filters)
        try:
            _queried = list(filter(lambda x: x[0] in specify, _queried))
        except TypeError:
            pass
        return _queried

    def _process_response(self, _signature: tuple, _collection: tuple, _response: memoryview) -> None:
        """
        :param _signature: (['index', 'endpoint'], {'request': "params", 'api': "key"})
        :param _collection:
        :return:
        """
        _update_ts = self.iso_local_utc()
        try:
            _data_label = '_'.join(_collection).upper()
            _one_dox = self.fallback_encoder(_update_ts, _decoded=(_data_label, _signature, _response))
            self._process_raw.append(_one_dox)
            self._total_rows_counter += len(_one_dox['Data'])
        except AttributeError:
            _denied = {k: v for k, v in zip(self._DENIED, [*_signature, dict(_response)])}
            self._bad_requests.append(dict(_denied))
        except Exception as e:
            raise e

    async def aio_queue(self):
        """

        :return:
        """
        while True:
            _signature, _resp = await self.response_queue.get()
            try:
                _collection = (_signature[1]['a'], _signature[1]['i'])
                self._process_response(_signature, _collection, _resp)
                self.response_queue.task_done()

            except KeyError:
                logger.warning(self._Co.format('196', '>>> UPDATING_ENDPOINTS'))
                self.mongo_drop_collection(self._HELPERS[0], check=False)
                _new_points = util_loads(_resp)

                for distill in _new_points:
                    distill['path'] = distill['path'].split('/')[-2:]

                self.mongo_insert_many(self._HELPERS[0], big_dump=_new_points)
                self.response_queue.task_done()

            logger.info(self._Co.format('11', f">>> PROCESSED:{_signature[0]}\n"))

    async def aio_writer(self, parameters: dict):
        logger.info(self._Co.format('196', f'>>> TOTAL_ROWS: {self._total_rows_counter}'))
        try:
            collection = f"{parameters['a']}_{parameters['i']}"
            # self.mongo_insert_many(collection, self._process_raw)
            for proc in self._process_raw:
                _write_success = proc[self._GET_DOX[1]][self._GET_DOX[2]]
                self._in_memory[collection].append(_write_success)
            self._process_raw.clear()
        except KeyError:
            logger.warning(self._Co.format('196', '* PASS.AIO_WRITER(endpt_write)'))


class GlassAIO(GlassHandler):

    _ROOT_DATA = "https://api.glassnode.com/v1/metrics"  # dataEndpoint
    _GEN_IGNORE = ('self', 'update', 'specify', 'prepped')  # -> self.glassnodes

    def __init__(self):
        super(GlassAIO, self).__init__()

    @staticmethod
    def set_params(
        *,
        a=None,
        s=None,
        u=None,
        i=None,
        f=None,
        c=None,
        e=None,
        timestamp_format=None
    ) -> Dict:
        """
        <<< Buffering Considerations >>>
         * BaseReference -> [24h x 5000items] = SAFE
         * 1h(max(208days)) -> [6Months||182days] = SAFE
         * 10m(max(35days)) -> [1Month||30days] = SAFE

        * EXAMPLE START/UNTIL TIMESTAMPS BELOW
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

        :return: Prepped Parameter Dictionary
        """
        _local_copy = locals().copy().items()
        _passed = dict(filter(lambda bx: bx[1] is not None, _local_copy))
        for _iso_8601 in filter(lambda elem: elem[0] in ['s', 'u'], _passed):
            _passed[_iso_8601] = int(parse_datetime(_passed[_iso_8601]).timestamp())
        _passed['timestamp_format'] = 'humanized'
        return _passed

    def _log_bad_requests(self, _denied_access: List) -> Any:
        if any(_denied_access):
            # self.mongo_insert_many(self._HELPERS[1], big_dump=_denied_access)
            self._bad_requests.clear()

    def dox_on_disk(self, _collection: tuple):
        """
        :param _collection: Near future working collection
        :return: 2 arrays; (known_bad_requests, already_saved)
        """
        (_sig, _field, _nest_field) = self._GET_DOX
        _bad_collection = zip(('Params.a', 'Params.i'), _collection)
        _filters = {"$and": [{_pax: {'$eq': _pix}} for _pax, _pix in _bad_collection]}
        _known_4xx = self.mongo_query(self._HELPERS[1], mon_filter=_filters, projector={_sig: True})
        _known_200 = f'{_collection[0]}_{_collection[1]}'
        _on_disk = self.mongo_query(_known_200, projector={_field: 1})
        return (
            [_bad[_sig][1] for _bad in _known_4xx],
            [_good[_field][_nest_field][1] for _good in _on_disk]
        )

    def query_requests(self, targeting: List[Tuple[str, str]], _params: Dict[str, Any]) -> None:
        """

        :param targeting:
        :param _params:
        :return:
        """
        _not_local = []
        _ref_collection = _params['a'], _params['i']
        _known_fails, _check_disk = self.dox_on_disk(_ref_collection)
        for _targets in targeting:
            skips = f'// SKIP(Known:BadRequest:4xx): {_targets} //'
            if _targets[1] in _known_fails:
                logger.warning(skips)
            elif _targets[1] in _check_disk:
                self._in_memory[_ref_collection].append(tuple(_targets))
            else:
                _not_local.append(_targets)
        if _not_local:
            self.api_key = self._API_KEY  # dotenv('GLASSNODE')
            self.pooled_aio(endpoints=_not_local, parameters=_params, base_url=self._ROOT_DATA)
            self._log_bad_requests(self._bad_requests)

    def glassnodes(
        self,
        prepped: dict, *,
        update: bool = None,
        specify: list = None,
        tier: str = '1/2/3',
        assets: str = 'BTC',
        currencies: str = 'NATIVE/USD',
        resolutions: str = "10m/1h/24h/1w/1month",
        formats: str = 'JSON'
    ):
        _locals_copy = locals().copy().items()
        _glass_quest = filter(lambda x: x[0] not in self._GEN_IGNORE, _locals_copy)
        _eps = self.load_endpoints(update, specify, _glass_quest)
        prepped = self.set_params(**prepped)
        self.query_requests(_eps, prepped)
        if self._in_memory:
            return dict(self._in_memory)


def test_suite(_gaio: GlassAIO, _periods: str = '24h'):
    _test = {'a': 'BTC', 'i': _periods, 'f': 'JSON', 'timestamp_format': 'humanized'}
    # _test = {'a': 'BTC', 's': '2021-06-01', 'i': _periods, 'f': 'JSON', 'timestamp_format': 'humanized'}
    # _test = [
    #     ('market', 'price_usd_ohlc'),
    #     # ('market', 'mvrv_more_155'),
    #     # ('market', 'price_usd_close'),
    #     # ('market', 'mvrv_less_155'),
    #     # ('market', 'price_usd'),
    # ]
    group_cast = [
        # 'mining',
        'fees',
        # 'market',
        # 'supply',
        # 'addresses',
        # 'indicators',
        # 'blockchain',
        # 'institutions',
        # 'transactions',
    ]
    try:
        # _fached.query_requests(formatted=_requesting, _params=_dikt)
        _robo = _gaio.glassnodes(prepped=_test, tier='1/2/3', resolutions=_periods, specify=group_cast)
    except Exception as e:
        raise e
    finally:
        _gaio.terminate_session()
        _gaio.kill_client()
    return _robo


if __name__ == '__main__':
    from pprint import pprint
    _live = GlassAIO()
    _response = test_suite(_live)
    time.sleep(0.125)
    print("\033[38;5;201m>>> Local Mongos Listing Below:\n")
    pprint(_response)


# def batch_metrics(self, preps: List[Tuple[Tuple[Any, Any], dict]]) -> Any:
#         async def _aio(target, params):
#             async with self._sesh() as session:
#                 async with session.get(target, params=params) as resp:
#                     _stats = (resp.status, resp.reason, str(resp.url), dict(resp.headers))
#                     if _stats[0] != 200:
#                         _fields = ['URL', 'Status', 'Header']
#                         _no_good = [_stats[2], f"<{_stats[0]}:{_stats[1]}>", _stats[3]]
#                         resp = [(*_bad,) for _bad in zip(_fields, _no_good)]
#                     else:
#                         resp = await resp.json(content_type=None)
#                     return resp
#         _ev_loop = asyncio.get_event_loop()
#         _params = {**preps[0][1], **self._API_KEY}
#         _coroutines = [_aio(f'{self._NODE}/{_ep[0]}/{_ep[1]}', _params) for _ep, _dk in preps]
#         return _ev_loop.run_until_complete(asyncio.gather(*_coroutines))

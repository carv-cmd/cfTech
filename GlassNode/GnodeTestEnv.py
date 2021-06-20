import logging
import asyncio
from datetime import datetime
from collections import defaultdict
from typing import Any, Dict, Tuple, List

from ciso8601 import parse_datetime, parse_rfc3339

from MongoDatabase.Mongos import MongoBroker
from EASYapi.RESTapi import AioHttpREST


__all__ = ['MongoHandler', 'GlassPoints', 'GlassAIO']


class MongoHandler(MongoBroker):

    _DOX_SCHEMA = ('Metric', 'Parameters', 'Updated', 'Data')
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
        _start = datetime.now()
        (_metric, _param, _process) = (_decoded[0], _decoded[1], _decoded[2])
        _set_len, _nest_key = (len(_process), ('v' if 'v' in _process[0] else 'o'))
        _overflow = []
        for _index in range(0, _set_len, _set_len // 10):
            try:
                _overflow = [k for k, v in _process[_index][_nest_key].items() if v > _max_int64]
            except AttributeError:
                if _process[_index][_nest_key] > _max_int64:
                    _fix = _process[_index][_nest_key]
                break
        if not _overflow:
            for xyz in _process:
                xyz['t'] = parse_rfc3339(xyz['t'])
        else:
            _encode_tuple = (_overflow, _nest_key, _process, *self._ENCODE_SCHEMA)
            _process = self._fallback_encoder(*_encode_tuple)
        _parameters = dict(zip(self._TUPLE_SIG, [*_param]))
        logging.info(f'-> ENCODING.TIME(<{(datetime.now() - _start).total_seconds()}>) -> {_metric}')
        return dict(zip(self._DOX_SCHEMA, [_metric, _parameters, _updated_at, _process]))

    def fallback_decoder(self, _json_encoded) -> Dict:
        """

        :param _json_encoded:
        :return:
        """
        try:
            _data_key = self._DOX_SCHEMA[-1:][0]
            _div_num, _div_key, _div_modified = self._DIV_KEYS
            _encoded = _json_encoded[_data_key]
            _nested = ('v' if 'v' in _encoded[_div_modified][0] else 'o')
            _decoded = self._fallback_decoder(
                _long_ki=_encoded[_div_key],        # DivKeys.class_key
                _latter_ki=_nested,                 # is (single|multi) part response?
                _encoded=_encoded[_div_modified],   # DivModified.class_key
                _mask=_encoded[_div_num]            # DivMask.class_key
            )
        except TypeError:
            _decoded = _json_encoded
        except Exception as e:
            raise e
        return _decoded


class GlassPoints(AioHttpREST, MongoHandler):

    # __slots__ = ('_in_memory', '_process_raw', '_bad_requests')

    _ROOT_METRICS = "https://api.glassnode.com/v2"  # -> metricsEndpoint
    _DENIED = ['Signature', 'Params', 'StatusHeader']  # -> write_requester.method
    _GET_DOX = ('Signature', 'Parameters', 'TuplePath')  # -> dox_on_disk/
    _API_KEY = 'GLASSNODE'

    def __init__(self):
        super(GlassPoints, self).__init__()
        self._in_memory = defaultdict(list)
        self._process_raw = []
        self._bad_requests = []

    def _endpt_updates(self, _updates: bool):
        self.mongo_drop_collection('GlassPoints', check=_updates)
        if self.api_key is None:
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
        _cox = 'GlassPoints'
        _projection = {'path': True}
        _cox = self.mongo_query(_cox, _gen_filter, _projection)
        return [idx['path'] for idx in _cox]

    def load_endpoints(self, update=None, specify=None, filters=None) -> List:
        """

        :param update:
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

    def _write_responses(self, _signature: zip, _collection: tuple) -> None:
        """

        :param _signature: request_signature: [('index', 'endpoint'), ]
        :param _collection:
        :return:
        """
        _update_ts = self.iso_local_utc()
        _collection = f'{_collection[0]}_{_collection[1]}'
        for _sig, _dox in _signature:
            try:
                _data_label = '_'.join(_sig[0]).upper()
                _one_dox = self.fallback_encoder(_update_ts, _decoded=(_data_label, _sig, _dox))
                self._process_raw.append(_one_dox)
            except ValueError:
                _denied = {k: v for k, v in zip(self._DENIED, [*_sig, dict(_dox)])}
                self._bad_requests.append(dict(_denied))
        if self._process_raw:
            self.mongo_insert_many(_collection, self._process_raw)
            for xyz in self._process_raw:
                _write_success = xyz[self._GET_DOX[1]][self._GET_DOX[2]]
                self._in_memory[_collection].append(_write_success)
            self._process_raw.clear()

    async def aio_writer(self, write_data: list, grouping: list, params: dict, x_lim_wait: float):
        _request_signature = [(grouped.split('/')[-2:], params) for grouped in grouping]
        try:
            _collection = (params['a'], params['i'])
            self._write_responses(zip(_request_signature, self.response_array), _collection)
        except KeyError:
            logging.warning("DID I CALL UPDATE?")
            _new_points = self.response_array.pop()
            for distill in _new_points:
                distill['path'] = distill['path'].split('/')[-2:]
            # self.mongo_insert_many('GlassPoints', big_dump=_new_points)
        self.response_array.clear()
        logging.info(f'X-Limit.sleep({x_lim_wait})')
        await asyncio.sleep(x_lim_wait)


class GlassAIO(GlassPoints):

    _ROOT_DATA = "https://api.glassnode.com/v1/metrics"  # dataEndpoint
    _GEN_IGNORE = ['self', 'update', 'specify', 'prepped']  # -> self.glassnodes

    def __init__(self):
        super(GlassAIO, self).__init__()

    def _log_bad_requests(self, _denied_access: List) -> None:
        if any(_denied_access):
            self.mongo_insert_many('BadRequests', big_dump=_denied_access)
            self._bad_requests.clear()

    def dox_on_disk(self, _collection):
        """
        :param _collection: Near future working collection
        :return: 2 arrays; (known_bad_requests, already_saved)
        """
        (_sig, _field, _nest_field) = self._GET_DOX
        _bad_collection = zip(('Params.a', 'Params.i'), _collection)
        _filters = {"$and": [{_px: {'$eq': _ax}} for _px, _ax in _bad_collection]}
        _bad_queries = self.mongo_query('BadRequests', mon_filter=_filters, projector={_sig: True})
        _good_collection = f'{_collection[0]}_{_collection[1]}'
        _on_disk = self.mongo_query(_good_collection, projector={_field: 1})
        return [_bad[_sig][1] for _bad in _bad_queries], \
               [_good[_field][_nest_field][1] for _good in _on_disk]

    def read_loader(self, formatted: List[Tuple[str, str]], _params: Dict[str, Any]) -> None:
        """

        :param formatted:
        :param _params:
        :return:
        """
        _not_local = []
        _ref_collection = _params['a'], _params['i']
        _known_fails, _check_disk = self.dox_on_disk(_ref_collection)
        for _targets in formatted:
            if _targets[1] in _known_fails:
                logging.warning(f'// SKIP(Known:BadRequest:4xx): {_targets} //')
            elif _targets[1] in _check_disk:
                self._in_memory[_ref_collection].append(tuple(_targets))
            else:
                _not_local.append(_targets)
        if _not_local:
            self.api_key = self._API_KEY
            self.pooled_aio(endpoints=_not_local, parameters=_params, base_url=self._ROOT_DATA)
            self._log_bad_requests(self._bad_requests)

    def glassnodes(
        self,
        prepped: dict,
        update: bool = None,
        specify: list = None,
        tier: str = '1/2/3',
        assets: str = 'BTC',
        currencies: str = 'NATIVE/USD',
        resolutions: str = "10m/1h/24h/1w/1month",
        formats: str = 'JSON'
    ) -> Dict:
        _locals_copy = locals().copy().items()
        _glass_quest = filter(lambda x: x[0] not in self._GEN_IGNORE, _locals_copy)
        _eps = self.load_endpoints(update, specify, _glass_quest)
        _prepped = self.set_params(**prepped)
        self.read_loader(_eps, _prepped)
        if self._in_memory:
            return dict(self._in_memory)

    def quick_delete(self, verify=False):
        _clear_collections = ['BTC_24h', 'BadRequests']
        for _nuked in _clear_collections:
            self.mongo_drop_collection(drop_col=_nuked, check=verify)

    @staticmethod
    def set_params(a=None, s=None, u=None, i=None, f=None, c=None, e=None, timestamp_format=None) -> Dict:
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

        :return: Prepped Parameter Dictionary
        """
        _local_copy = locals().copy().items()
        _passed = dict(filter(lambda bx: bx[1] is not None, _local_copy))
        for _iso_8601 in filter(lambda elem: elem[0] in ['s', 'u'], _passed):
            _passed[_iso_8601] = int(parse_datetime(_passed[_iso_8601]).timestamp())
        _passed['timestamp_format'] = 'humanized'
        return _passed


def covid_test(_parameters: dict, indices: list, resetting: bool = None):
    glass_api = GlassAIO()
    _foobars = glass_api.glassnodes(_parameters, specify=indices)
    if resetting:
        glass_api.quick_delete(resetting)
    glass_api.kill_client()
    glass_api.terminate_session()
    return _foobars


if __name__ == '__main__':
    from pprint import pprint
    _config = {'a': 'BTC', 'i': '24h', 'f': 'JSON', 'timestamp_format': 'humanized'}
    query_for = ['fees']
    covid_test(_config, indices=query_for)


# def batch_metrics(self, preps: List[Tuple[Tuple[Any, Any], dict]]) -> Any:
    #     """
    #
    #     :param preps:
    #     :return:
    #     """
    #     async def _aio(target, params):
    #         async with self._sesh() as session:
    #             async with session.get(target, params=params) as resp:
    #                 _stats = (resp.status, resp.reason, str(resp.url), dict(resp.headers))
    #                 if _stats[0] != 200:
    #                     _fields = ['URL', 'Status', 'Header']
    #                     _no_good = [_stats[2], f"<{_stats[0]}:{_stats[1]}>", _stats[3]]
    #                     resp = [(*_bad,) for _bad in zip(_fields, _no_good)]
    #                 else:
    #                     resp = await resp.json(content_type=None)
    #                 return resp
    #     _ev_loop = asyncio.get_event_loop()
    #     _params = {**preps[0][1], **self._API_KEY}
    #     _coroutines = [_aio(f'{self._NODE}/{_ep[0]}/{_ep[1]}', _params) for _ep, _dk in preps]
    #     return _ev_loop.run_until_complete(asyncio.gather(*_coroutines))

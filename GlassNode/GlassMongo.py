# import numpy
# import timeit
# import numba
# from functools import reduce
# from time import ctime
import pandas
from GlassNodeBroker import Glassnodes, Thread, Queue, Any, Dict


class GlassHelper(Glassnodes):

    def get_endpoints(self, specified: Dict = None, projector=None, updates=False):  # -> List:
        """
        :param specified: ex. { $and: [{"tier": 1}, {"assets.symbol": {"$eq": 'BTC'}}]}
        :param updates: if true, db.GlassPoints.drop, db.GlassPoints.insert(request); else db.loader
        :return: List[Dicts[endpoint_data]]
        """
        try:
            self.mongo_drop_collection('GlassPoints', check=updates)
            _recent = self._request('GET', target=self._HELPER, params={'a': '_null_'})[0].json()
            for eps in _recent:
                eps['path'] = eps['path'].split('/')[-2:]
            self.mongo_insert_many(big_dump=_recent, col_name='GlassPoints')
        except AssertionError:
            self.set_collection(collection_name='GlassPoints')
        if specified:
            _finder = self.working_col.find(specified, projection=projector)
        else:
            _finder = self.working_col.find(projection={'_id': False})
        return list(_finder)

    def endpoint_help(self, tier: str, asset: str,
                      currencies: str, resolutions: str,
                      formatting: str, update: bool,
                      query_proj: dict = None) -> Any:
        _endpoint_query = {
            "$and": [
                {"tier": {"$in": [int(n) for n in tier.split('/')]}},
                {"assets.symbol": {"$in": asset.upper().split('/')}},
                {'currencies': {"$in": currencies.upper().split('/')}},
                {"resolutions": {"$in": resolutions.split('/')}},
                {"formats": {"$in": formatting.upper().split('/')}}]
        }
        query_proj = {
            'tier': False, 'assets': False, 'currencies': False, 'resolutions': False, 'formats': False
        }
        return [elem['path'] for elem in self.get_endpoints(
            specified=_endpoint_query, projector={**{'_id': False}, **query_proj}, updates=update)]

    def quick_query(self,
                    tier: str = '1/2/3',
                    asset: str = 'BTC',
                    currencies: str = 'NATIVE/USD',
                    resolutions: str = "10m/1h/24h/1w/1month",
                    formatting: str = 'JSON/CSV',
                    update: bool = False,
                    search: list = None,
                    initialize: dict = None):
        """
        Query Glassnode indices/endpoints for available options.
        Any grouped function parameters should be separated by '/' symbol for safe split.

        :param tier: str = '1/2/3'
        :param asset: str = 'BTC/ETH'
        :param currencies: str = 'NATIVE/USD'
        :param resolutions: str = '10m/1h/24h/1w/1month'
        :param formatting: str = 'JSON/CSV'
        :param update: bool = 'True' to update stored endpoints
        :param search: list = available glassnode indices to return
        :param : dict = pass to prep glass_quest signature in one call (applies-like-params)
        :return: Given query filter returns all endpoints for it either semi/fully prepped
        """
        _match = self.endpoint_help(
            **dict(filter(lambda x: x[0] not in ['self', 'search', 'initialize'], locals().copy().items())))
        if search is not None:
            _match = list(filter(lambda x: x[0] in search, _match))
        if initialize is not None:
            for mx in _match:
                mx.append(initialize)
        return _match


class GlassMongoAPI(GlassHelper, Glassnodes):

    def __init__(self):
        super(GlassMongoAPI, self).__init__()
        self._pandas_queue = Queue()

    def update_collection(self):
        pass

    def glass_pandas(self):
        pandas.set_option('display.width', 120)
        # TODO timeit (git_implementation) vs (my_implementation)
        #  * df = pd.DataFrame(json.loads(r.text))
        #  * df = df.set_index('t')
        #  * df.index = pd.to_datetime(df.index, unit='s')
        #  * df = df.sort_index()
        #  * s = df.v
        #  * s.name = '_'.join(url.split('/')[-2:])
        #  * return s
        for elem in self.loaded:
            _metric, _data = elem[1]['_metrics'], elem[1]['_data']
            try:
                frame_keys = ['t'] + list(_data[0]['o'].keys())
                framed = pandas.DataFrame(
                    data=[{k: (_data[iters]['t'] if k in 't' else _data[iters]['o'][k])
                           for k in frame_keys} for iters in range(len(_data))],
                    columns=frame_keys)
            except KeyError:
                framed = pandas.DataFrame(_data)
            framed.set_index('t', inplace=True)
            framed.index = pandas.to_datetime(
                framed.index.to_flat_index(), unit='s', infer_datetime_format=True)
            framed.sort_index(inplace=True)
            framed.name = _metric
            print(framed.name)
            print(framed)

    def glass_mongo(self, _rapid_query):
        """ ('mining', 'difficulty_mean', {'a': 'BTC'}) -> wildly overFlows """
        _degen_magic = Thread(name='_APP_LEVEL', target=self.magic_metrics(_rapid_query))
        _degen_magic.start()
        _degen_magic.join()
        self.external_flag.wait()
        return self.loaded

    def flush_mongo(self, dropping: Any = None, checked=True):
        try:
            self.mongo_drop_collection(check=checked)
        except TypeError:
            self.mongo_drop_collection(drop_col=dropping, check=checked)

# def time_gator(foo_gas: Glassnodes):
#     """
#     1). Response(UTC):
#             * humanized rfc3339 -> str('2021-05-15T00:00:00Z')
#
#     2). Stage1(UTC):
#             * ciso8601.parse_rfc3339  -> dt.obj(2021-05-15 00:00:00+00:00)
#
#     3). Stage2(UTC):
#             * localtime.fromutctimestamp(ciso8601.parse_rfc3339)
#     """
#
#     gator = foo_gas.get_metrics(
#         index='indicators',
#         endpoint='difficulty_ribbon',
#         a='BTC',
#         s=int(foo_gas.ciso_handler('2021-05-15')),
#         i='24h',
#         timestamp_format='humanized'
#     )
#
#     gator = gator[0].json()[15]['t']
#
#     print('\n', type(gator), gator)
#
#     ciso_gator = ciso8601.parse_rfc3339(gator)
#
#     print('\n', type(ciso_gator), ciso_gator)
#
#     print('\n', type(ctime(ciso_gator.timestamp())), ctime(ciso_gator.timestamp()))
#
#     utc_gator = datetime.utcfromtimestamp(ciso_gator.timestamp())
#
#     print('\n', type(ciso_gator), utc_gator)
#
#     print('\n', type(ciso_gator.ctime()), ciso_gator.tzname())


if __name__ == '__main__':
    from pprint import pprint

    # gh = GlassHelper()
    gapi = GlassMongoAPI()
    gapi.get_loaded()

    a, r = 'BTC', '24h'
    yeet = gapi.quick_query(
        search=['indicators'],
        initialize={'a': a, 'i': r}
    )
    # pprint(yeet, width=120)
    gapi.glass_mongo(yeet[20:25])

    # foobats = yeet[:25]
    # foobats[0].append({'a': "BTC", 'i': "24h"})
    # gapi.glass_mongo(foobats)



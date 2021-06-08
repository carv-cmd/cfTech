# import numpy
# import timeit
# import numba
# from functools import reduce
import pandas
from time import time, ctime
from GlassNodeBroker import Glassnodes, ciso8601, datetime, Thread, Queue, Any


class GlassHelper(Glassnodes):

    def endpoint_help(self, tier: str, asset: str,
                      currencies: str, resolutions: str,
                      formatting: str, update: bool) -> Any:
        _endpoint_query = {
            "$and": [
                {"tier": {"$in": [int(n) for n in tier.split('/')]}},
                {"assets.symbol": {"$in": asset.upper().split('/')}},
                {'currencies': {"$in": currencies.upper().split('/')}},
                {"resolutions": {"$in": resolutions.split('/')}},
                {"formats": {"$in": formatting.upper().split('/')}}]
        }
        return [
            {'matched': dict(filter(lambda elem: elem[0] not in ['assets'], endpts.items()))}
            for endpts in list(self.get_endpoints(specified=_endpoint_query, updates=update))]

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
            **dict(filter(lambda x: x[0] not in ['self', 'search', 'prepare'], locals().copy().items())))
        self.kill_client()
        print(_match)

        if search is None:
            search = list(set(map(lambda idx: idx['matched']['path'].split('/')[-2:-1][0], _match)))
            print(search)
        print()
        try:
            assert initialize is None, 'prepare != None'
            prep_map = map(lambda m: m['matched']['path'].split('/')[-2:], _match)
        except AssertionError as e:
            prep_map = map(lambda m: (*m['matched']['path'].split('/')[-2:], initialize), _match)
        return list(filter(lambda pe: pe[0] in search, prep_map))


class GlassMongoAPI(Glassnodes):
    def __init__(self):
        super(GlassMongoAPI, self).__init__()
        self._pandas_queue = Queue()

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
        return self.loaded

    def flush_mongo(self, dropping: Any = None, checked=True):
        try:
            self.mongo_drop_collection(check=checked)
        except TypeError:
            self.mongo_drop_collection(drop_col=dropping, check=checked)


def time_gator(foo_gas: Glassnodes):
    """
    1). Response(UTC):
            * humanized rfc3339 -> str('2021-05-15T00:00:00Z')

    2). Stage1(UTC):
            * ciso8601.parse_rfc3339  -> dt.obj(2021-05-15 00:00:00+00:00)

    3). Stage2(UTC):
            * localtime.fromutctimestamp(ciso8601.parse_rfc3339)
    """

    gator = foo_gas.get_metrics(
        index='indicators',
        endpoint='difficulty_ribbon',
        a='BTC',
        s=int(foo_gas.ciso_handler('2021-05-15')),
        i='24h',
        timestamp_format='humanized'
    )

    gator = gator[0].json()[15]['t']

    print('\n', type(gator), gator)

    ciso_gator = ciso8601.parse_rfc3339(gator)

    print('\n', type(ciso_gator), ciso_gator)

    print('\n', type(ctime(ciso_gator.timestamp())), ctime(ciso_gator.timestamp()))

    utc_gator = datetime.utcfromtimestamp(ciso_gator.timestamp())

    print('\n', type(ciso_gator), utc_gator)

    print('\n', type(ciso_gator.ctime()), ciso_gator.tzname())



if __name__ == '__main__':
    from pprint import pprint
    # GAS_NODES = GlassMongoAPI()
    # GAS_NODES.flush_mongo('BTC_24H')

    gh = GlassHelper()
    a, r = 'BTC', '24h'
    yeet = gh.quick_query(
        tier='1/2/3',
        asset=a,
        resolutions=r,
        search=['market'],
        initialize={'a': a, 's': '2020-01-01', 'i': r}
    )
    pprint(yeet, width=120)


    # GATORS = GAS_NODES.glass_mongo(btc_tuples[0:29])
    # print(GATORS)

    # pprint(btc_tuples)  # [0:30])
    # RACKED = [('indicators', 'difficulty_ribbon', {'a': 'BTC', 'i': '24h'})]
    # asshole = GAS_NODES.glass_mongo(RACKED)

    # GAS_NODES.glass_pandas()
    # print(racked)

    # pprint(gassed, depth=3)
    # glass_test(GAS_NODES, rapids)
    # clean_glass(GAS_NODES)


    # _line = f"\n{''.join(['_' for e in range(90)])}"
    # batch_queries = [
    #     {'tier': 1, 'asset': 'BTC', 'currencies': 'NATIVE/USD', 'resolutions': '24h'},
    #     {'tier': 2, 'asset': 'ETH', 'currencies': 'NATIVE', 'resolutions': '10m/1month'},
    #     {'tier': 3, 'asset': 'BTC', 'currencies': 'NATIVE/USD', 'resolutions': '10m/24h'},
    #     {'tier': 3, 'asset': 'ETH', 'currencies': 'NATIVE/USD', 'resolutions': '10m'},
    #     {'tier': 3, 'asset': 'ETH', 'currencies': 'NATIVE', 'resolutions': '1month'}
    # ]
    # _xyz = endpoints(**batch_queries[0], update=True)
    # print(f"\nLenQuery({len(_xyz)}) -> Given -> {batch_queries[0]}{_line}\n")
    # pprint(_xyz, )
    # fached = [endpoints(**racked) for racked in batch_queries]
    # for cooked, beans in enumerate(fached):
    #     print(f"\nLenQuery({len(beans)}) -> Given -> {batch_queries[cooked]}{_line}\n")
    #     pprint(beans, indent=2)
    #     print(_line)

# def numba_test(low_level: _GlassBroker):
#     _rapid = ('indicators', 'difficulty_ribbon', {'a': 'BTC'})
#     _jit_response = low_level.get_metrics(index=_rapid[0], endpoint=_rapid[1], **_rapid[2])
#     jit_test = (_jit_response[0], 'DONKEY_BONER', 'CAT_BUTTHOLE')
#     for fuk in range(5):
#         print('>>> Encoding. . .')
#         low_level.glass_encoder(jit_test)
#         print('>>> Finished. . .')
#
#     # _resi = low_level.glass_encoder(_jit_response)['_data']['_divModified']
#     # xyz = [_resi[utg] for utg in range(0, len(_resi), 100)]
#     # pprint(xyz)

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

# import numpy
# import timeit
# import numba
import pandas

from GlassNodeBroker import Glassnodes, Tuple, Thread, Queue


class GlassHelper(Glassnodes):
    def endpoint_help(self,
                      tier: str = '1/2/3',
                      asset: str = 'BTC/ETH',
                      currencies: str = 'NATIVE/USD',
                      resolutions: str = "10m/1h/24h/1w/1month",
                      formatting: str = 'JSON/CSV',
                      update: bool = False) -> Tuple:
        _endpoint_query = {
            "$and": [
                {"tier": {"$in": [int(n) for n in tier.split('/')]}},
                {"assets.symbol": {"$in": asset.upper().split('/')}},
                {'currencies': {"$in": currencies.upper().split('/')}},
                {"resolutions": {"$in": resolutions.split('/')}},
                {"formats": {"$in": formatting.upper().split('/')}}]
        }
        return _endpoint_query, [
            {'Endpt.Params': dict(filter(lambda elem: elem[0] not in ['_id', 'assets'], endpts.items())),
             'Endpt.Assets': list(filter(lambda full: full['symbol'] in asset.upper(), endpts['assets']))}
            for endpts in list(self.get_endpoints(specified=_endpoint_query, updates=update))]


class GlassMongoAPI(Glassnodes):
    def __init__(self):
        super(GlassMongoAPI, self).__init__()
        self._pandas_queue = Queue()

    def glass_mongo(self, _rapid_query):
        """ ('mining', 'difficulty_mean', {'a': 'BTC'}) -> wildly overFlows """
        _degen_magic = Thread(name='_APP_LEVEL', target=self.magic_metrics(_rapid_query))
        _degen_magic.start()
        _degen_magic.join()
        return self._loaded

    def json_to_df(self, _metric, _data):
        pandas.set_option('display.width', 120)
        # TODO timeit (git_implementation) vs (my_implementation)
        #  * df = pd.DataFrame(json.loads(r.text))
        #  * df = df.set_index('t')
        #  * df.index = pd.to_datetime(df.index, unit='s')
        #  * df = df.sort_index()
        #  * s = df.v
        #  * s.name = '_'.join(url.split('/')[-2:])
        #  * return s
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
        return framed


def q_test(tier=None, asset=None, currencies=None, resolutions=None, formatting=None, update=False):
    _passed_in = locals().copy()
    helping = GlassHelper()
    _lines = ''.join(['-' for i in range(90)])
    _mon_filter, _matched = helping.endpoint_help(
        **dict(filter(lambda f: f[1] is not None, _passed_in.items())))
    helping.kill_client()
    print(f'\n* QUERY_FILTER:')
    pprint(_mon_filter, indent=2)
    print(f"\nFOUND -> [<{len(_matched)}>] VALID ENDPOINTS\n{_lines}\n")
    # pprint(_matched, indent=2)
    return _matched


def clean_glass(gas_nodes):
    gas_nodes.mongo_drop_collection(drop_col='BTC_24H', check=True)


def glass_test(gas_nodes, _rapids=None):
    gasser = gas_nodes.glass_mongo(_rapid=_rapids)
    for i in gasser:
        try:
            print(i['_metrics'])  # , i[0]['_data'][0])
            print('DATABASE')
        except TypeError:
            print(i[0]['_metrics'])  # , i[0]['_data']['_divModified'][0])
            print('REQUESTED')


if __name__ == '__main__':
    from pprint import pprint
    t, a, r, f = '1', 'BTC', '24h', 'JSON'
    btc_tuples = q_test(tier=t, asset=a, resolutions=r, formatting=f)
    redux = [(*btc['Endpt.Params']['path'].split('/')[-2:], {'a': a, 'i': r}) for btc in btc_tuples]
    pprint(redux)

    # GAS_NODES = GlassMongoAPI()
    # gassed = GAS_NODES.glass_mongo(_rapid=redux)
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

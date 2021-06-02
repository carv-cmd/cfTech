# import matplotlib.dates as mdates
# import mongoDB.Mongos
import matplotlib.pyplot as plt
from matplotlib import style

from GlassNodeBroker import *

logging.getLogger('matplotlib').setLevel(logging.ERROR)


class MatPlotLibs(Glassnodes):
    _growler = ''.join(['-' for i in range(50)])

    style.use('dark_background')

    def __init__(self, big_queries: List[Any] = None):
        super().__init__()
        self._queries = big_queries
        # self.big_plot = plt.subplots(nrows=1, ncols=1, figsize=(6, 9))

    @staticmethod
    def _make_subplots(**kwargs):
        return plt.subplots(subplot_kw=kwargs)

    @staticmethod
    def get_plt_params():
        print(plt.rcParams)

    def _loader_plt(self, dp):
        #     # plt.suptitle('GlassNode: Apes-Linked-Api')
        #     for result in dp:
        #         for col_key in result.keys():
        #             print(f'\n{self._growler}\nresult[col_key]: {result[col_key]}')
        #         plt.plot(result[col_key], label=f'{result.name}.{col_key}')
        #         plt.yscale('symlog', linthresh=('2008', '2014'))
        #
        # plt.xlabel('Time Series')
        # plt.ylabel('Apes')
        # fig = plt.gcf()
        # fig.set_size_inches(9, 6, forward=True)
        # # plt.legend(loc='upper left')
        # plt.tight_layout()
        # plt.show()
        pass

    def run_glassnodes(self, query_metrics=None):
        if self._queries is not None:
            query_metrics = self._queries
        self._loader_plt(self.magic_metrics(query_metrics))


def big_query(queries, mats=False):
    _known = {
        '0': ('market', 'price_usd_close', {'a': "BTC"}),
        '1': ('market', 'price_usd_ohlc', {'a': "BTC"}),
        '2': ('market', 'marketcap_realized_usd', {'a': 'BTC'}),
        '3': ('market', 'price_drawdown_relative', {'a': 'BTC'}),
        '4': ('market', 'marketcap_usd', {'a': "BTC"}),
        '5': ('market', 'mvrv_z_score', {'a': "BTC"}),
        '6': ('market', 'price_realized_usd', {'a': "BTC"}),
        '7': ('supply', 'active_more_1y_percent', {'a': 'BTC'}),
        '8': ('supply', 'current', {'a': 'BTC'}),
        '9': ('blockchain', 'block_height', {'a': 'BTC'}),
        '10': ('indicators', 'stock_to_flow_ratio', {'a': 'BTC'}),
        '11': ('indicators', 'hash_ribbon', {'a': 'BTC'}),
        '12': ('indicators', 'difficulty_ribbon', {'a': 'BTC'}),
        '13': ('indicators', 'realized_profit', {'a': 'BTC'}),
        '14': ('indicators', 'realized_loss', {'a': 'BTC'}),
        '15': ('indicators', 'reserve_risk', {'a': 'BTC'}),
        '16': ('transactions', 'transfers_from_exchanges_count', {'a': 'BTC'}),
        '17': ('transactions', 'transfers_to_exchanges_count', {'a': 'BTC'})
    }
    _getters = [_known[index] for index in queries]
    if mats:
        pass
    else:
        heavy_wizard = Glassnodes()
        heavy_wizard.magic_metrics(_getters)


if __name__ == '__main__':
    big_query(['0'])

    # NODES = MatPlotLibs()
    # NODES.magic_metrics(_known)
    #
    # NODES.run_glassnodes(_testing)

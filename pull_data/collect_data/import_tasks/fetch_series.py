from api_config import *
from interval_config import *
from ticker_config import *
from pprint import pprint

from alpha_vantage.timeseries import TimeSeries


class SeriesCall(APIConfig, TickConfig):
    def __init__(self):
        super(SeriesCall, self).__init__()
        self.series = TimeSeries()

    def initialize_fetch(self):
        self.series = TimeSeries(key=self.get_api_key(), output_format=self.get_forma())

    def fetch_intraday(self):
        daters, metas = self.series.get_intraday(symbol=self.get_symbol(), interval=self.get_unit(),
                                                 outputsize=self.get_size())
        return daters, metas

    def fetch_daily(self):
        daters, metas = self.series.get_daily(symbol=self.get_symbol(), outputsize=self.get_size())
        return daters, metas

    def fetch_weekly(self):
        daters, metas = self.series.get_weekly(symbol=self.get_symbol())
        return daters, metas

    def fetch_monthly(self):
        daters, metas = self.series.get_monthly(symbol=self.get_symbol())
        return daters, metas


def series_fetch(tick):
    key = APIConfig().set_api_key("ALPHAVANTAGE_API_KEY")
    foo = TickConfig()
    mf = SeriesCall()

    mf.set_api_key(key)
    mf.set_size(foo.get_size())
    mf.set_units(foo.get_unit())
    mf.set_size(foo.get_size())
    mf.set_forma(foo.get_forma())

    mf.set_symbol(tick)
    mf.initialize_fetch()

    return mf.fetch_intraday()


if __name__ == "__main__":
    tick_list = ['AAPL', 'MSFT', 'AMZN']
    re_list = []

    for tick in tick_list:
        fuk = series_fetch(tick)
        print('\n--------------------------------------------------\n')
        pprint(fuk[1])
        print()
        pprint(fuk[0])
        print('\n--------------------------------------------------')



#########################################################################
#########################################################################
# def intra_fetcher(key, ticker, unit='60min', size='compact'):
#     mf.set_auto(key)
#     mf.set_symbol(ticker)
#     mf.set_units(unit)
#     mf.set_size(size)
#     mf.initialize_fetch()
#     mf.fetch_intraday()
#     return mf
#
#
# #########################################################################
# #########################################################################
# if __name__ == "__main__":
#     foo = APIConfig()
#     foo.set_api_key("ALPHAVANTAGE_API_KEY")
#
#     ticker_list = ['AAPL', 'MSFT', 'AMZN']
#     ret_list = []
#     for tick in ticker_list:
#         mf = SeriesCall()
#         intra_fetcher(foo.get_api_key(), tick)

#########################################################################
#########################################################################
# def fetcher(ticker, mf):
#     # mf = FetchTimeSeries()
#
#     mf.set_api_key("ALPHAVANTAGE_API_KEY")
#
#     mf.set_symbol(f"{ticker}")
#     mf.set_units('1min')
#     mf.set_size('compact')
#
#     mf.initialize_fetch()
#
#     return mf.fetch_intraday()
#
#
# if __name__ == "__main__":
#     # ticker_list = ['AAPL', 'MSFT', 'AMZN', 'TSLA', 'FB', 'GOOG',
#     #                'GOOGL', 'NVDA', 'ADBE', 'PYPL', 'GLXY']
#
#     ticker_list = ['AAPL', 'MSFT']
#     return_list = []
#     try:
#         for iex in ticker_list:
#             return_daters = fetcher(iex, SeriesCall())
#             return_list.append(return_daters)
#             print(f'Appended: {iex} data')
#
#         print(return_list)
#
#     except ValueError:
#         print(return_list)

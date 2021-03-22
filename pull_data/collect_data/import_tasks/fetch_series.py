from api_config import *
from pprint import pprint
from alpha_vantage.timeseries import TimeSeries


class SeriesCall(KeyConfig):
    def __init__(self):
        super().__init__()
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


#########################################################################
#########################################################################
def quick_set(**kwargs):

    def keyless():
        apikey = KeyConfig()
        apikey.set_api_key(kwargs['api_key'])
        return apikey.get_api_key()

    def setup_config():
        mf.hold_key(access)
        mf.set_units(kwargs['interval'])
        mf.set_size(kwargs['output'])
        mf.set_forma(kwargs['forma'])
        return mf

    access = keyless()
    mf = SeriesCall()
    return setup_config()


def caller(tik):
    io = quick_set(**kwargs)
    io.set_symbol(tik)
    return io


#########################################################################
#########################################################################
kwargs = {"api_key": 'ALPHAVANTAGE_API_KEY',
          "interval": '1min',
          "output": 'compact',
          "forma": 'pandas'}


if __name__ == "__main__":
    tick_list = ['AAPL', 'NVDA']  # , 'AMD', 'TSLA']

    for tick in tick_list:
        calling = caller(tick)
        calling.initialize_fetch()
        a1, a2 = calling.fetch_monthly()
        print('\n-----------------------------------------------------------------------')
        pprint(a2)
        print()
        pprint(a1)

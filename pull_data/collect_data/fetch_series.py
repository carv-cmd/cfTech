from configure_fetch import *
from alpha_vantage.timeseries import TimeSeries
from pprint import pprint
# from alpha_vantage.cryptocurrencies import CryptoCurrencies


#########################################################################
#########################################################################
class FetchTimeSeries(Configs, StepSize):
    def __init__(self):
        super().__init__()
        self.series = TimeSeries()

    def initialize_fetch(self):
        self.series = TimeSeries(key=self.get_api_key(), output_format=self.get_forma())

    def fetch_data(self):
        daters, metas = self.series.get_intraday(symbol=self.get_symbol(), interval=self.get_unit(),
                                                 outputsize=self.get_unit())
        return daters, metas


#########################################################################
#########################################################################
def fetcher():
    mf = FetchTimeSeries()

    ticker = 'NVDA'

    mf.set_api_key("ALPHAVANTAGE_API_KEY")
    mf.set_symbol(ticker)
    mf.set_units('1min')
    mf.set_size('compact')

    print(mf)

    mf.initialize_fetch()

    return mf.fetch_data()


if __name__ == "__main__":
    pprint(fetcher())

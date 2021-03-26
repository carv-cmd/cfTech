import os
import requests
import datetime
from dotenv import load_dotenv, find_dotenv
from call_threader import *

load_dotenv(find_dotenv())

print(f"\nInitializing REST API Caller...")


class CurrentPrice:
    """ Descriptor class for call CryptoCompare single-symbol-price """
    def __init__(self, **kwargs):
        self.payload = kwargs
        self.fsym = kwargs['fsym']
        self.tsyms = kwargs['tsyms']
        self.data_points = {f"{datetime.date.today()}": f"{self.tsyms}-{self.fsym}-PRICE_DATA"}

    def __set__(self, instance, **kwargs):
        self.payload = kwargs

    def __str__(self):
        return f"\nRequest Payload:\n{self.payload}"


class CryptoCompare(CurrentPrice):

    configs = CurrentPrice

    def single_price(self):
        try:
            t = datetime.datetime.now()
            key = "{}".format(datetime.time(t.hour, t.minute, t.second,
                                            t.microsecond).isoformat(timespec='microseconds'))

            req = requests.get("https://min-api.cryptocompare.com/data/price",
                               headers=headers, params=self.payload).json()

            self.data_points[key] = req

            print(f'\n{key} = {self.data_points[key]}')

        except TypeError or KeyError or ConnectionRefusedError or ConnectionError:
            print("LENGTHEN REQUEST INTERVAL")

    def print_dict(self):
        print(f'\n------------------------------------------'
              f'\n{self.fsym} Dictionary:\n')
        for key in self.data_points.keys():
            print(f'{key}: {self.data_points[key]}')


def persist_until(period=5, timer=30):
    """ It will hang when an exceptions raised, need to fix that.. """
    @set_interval(interval=period)
    def persistent_until():
        cc.single_price()

    stopper = persistent_until()

    time.sleep(timer)
    stopper.set()


def config_payload(fsym='', tsyms='', exchange='cccagg_or_exchange', extras=__name__):
    """
    :param: payload: params of the api url string
    :param: fsym: cryptocurrency symbol of interest
    :param: exchange: exchange to obtain data from
    :param: tsyms: comma separated cryptocurrency symbols list to convert into
    """

    return {'fsym': fsym,
            'tsyms': tsyms.split(','),
            'e': exchange,
            'extraParams': extras}


apikey = os.getenv("CCOMPARE_DATA_API_KEY")
headers = {"authorization": 'Apikey'+apikey}


if __name__ == "__main__":
    configurations = config_payload(fsym='BTC', tsyms='USD,EUR')
    cc = CryptoCompare(**configurations)
    persist_until(period=1, timer=60)
    cc.print_dict()

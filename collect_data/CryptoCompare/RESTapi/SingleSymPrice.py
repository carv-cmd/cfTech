import os
import requests
import datetime
from dotenv import load_dotenv, find_dotenv
from RESTapi.call_threader import *
splitter = '------------------------------------------'

load_dotenv(find_dotenv())

apikey = os.getenv("CCOMPARE_DATA_API_KEY")
endpoint = "https://min-api.cryptocompare.com/data/price"


class CurrentPrice:
    """ Descriptor class for call CryptoCompare single-symbol-price """
    def __init__(self, **kwargs):
        self.payload = dict()
        self.fsym = kwargs['fsym']
        self.tsyms = kwargs['tsyms']
        self.dater_dict = {f"{datetime.date.today()}": f"{self.fsym}-{self.tsyms}-PRICE"}

    def __get__(self, instance, owner):
        return self.dater_dict

    def __set__(self, instance, **kwargs):
        self.payload = kwargs

    def __str__(self):
        return f"\nRequest Payload:\n{self.payload}"


class CryptoCompare(CurrentPrice):

    r = requests.models.Response

    def single_price(self):
        """
        *** response latency largely determined by client ISP, connection, caching, etc... ***
        Appends price-data from response to dictionary bound to object instance
        :param: key: ISO-formatted current time; this is automatically set when functions called
        :param: r: 'requests.models.Response' obj, or the REST API response object
        :param: req: 'requests.models.Response' converted into a 'json' object for dictionary storage
        :returns: None, class method, modifies object CryptoCompare object instance
        DictFormat:     dater_dict: {'request-date': asset-conversion-data,
                                     'request-time': response-value, ->}
        """
        try:
            t = datetime.datetime.now()
            key = "{}".format(datetime.time(t.hour, t.minute, t.second,
                                            t.microsecond).isoformat(timespec='microseconds'))

            self.r = requests.get(endpoint, params=self.payload)
            print(f'RequestTime: [<{key}>]: {self.r}')

            req = self.r.json()
            self.dater_dict[key] = req

        except TypeError or KeyError or ConnectionRefusedError or ConnectionError:
            print('Raised Handler: <U-FUK-UP>')
            raise

    def print_dict(self):
        """
        TODO Compile all the mini json responses into one large json response, push to DB
        Iterates through the dictionary created by the class method printing all key/value pairs
        *** More efficient to make-dict-to-json-pushDB or the 'TO/DO' method??? ***
        """
        print(f'{splitter}\n{self.fsym} Dictionary:')
        for key in self.dater_dict.keys():
            print(f'{splitter}\n{key}: {self.dater_dict[key]}')

    def __str__(self):
        """ Expected Response Code: <Response [200]> """
        return f'\n{splitter}\nRequest URL:\n{self.r.url}'


def persist_until(period=1.0, timer=8):
    """ It will hang when an exceptions raised, need to fix that.. """
    @set_interval(interval=period)
    def persistent_until():
        cc.single_price()

    stopper = persistent_until()

    time.sleep(timer)
    stopper.set()


def config_payload(fsym='', tsyms='', exchange='cccagg_or_exchange', extras="SingleSymPrice"):
    """
    'payload' is just the params
    :param: fsym: cryptocurrency symbol of interest
    :param: tsyms: n>=1 currency conversions passed as comma separated string, ex. 'USD,EUR,BTC'
    :param: exchange: exchange to obtain data from (** add_exchange_list **)
    :param: extras: project-name, default=SingleSymPrice
    """
    return CryptoCompare(**{'fsym': fsym,
                            'tsyms': tsyms.split(','),
                            'e': exchange,
                            'extraParams': extras,
                            'api_key': apikey})


if __name__ == "__main__":
    print(f"\nInitializing <SingleSymPrice> REST Connection...\n")

    cc = config_payload(fsym='BTC', tsyms='USD,EUR')
    cc.single_price()
    persist_until()
    print(cc.dater_dict)
    cc.print_dict()

else:
    print(f'\nInitiated Helper Module: "{__name__}"')

# def get_query(self, endpoint: str, a: str = None, s: int = None, u: int = None,
# i: str = None, f: str = None, c: str = None, e: str = None, ts_format: str = 'UNIX'):
# * pandas.read_json(json.dumps(response), convert_dates=['t'])
# *-> ^useful when loading from db/disk for matplotlib-ing
# from typing import DefaultDict, Any, List
import os
import logging
import json
import requests
from collections import defaultdict
from pprint import pprint
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s')

__all__ = ['Glassnodes', 'logging', 'json']


class GlassnodeBroker(object):
    _GLASS = "https://api.glassnode.com/v1/metrics/"
    _session = requests.Session()

    def __get__(self, instance, owner=None):
        jive_ass_foo = f'{self._GLASS}{instance.endpoint}'  # {instance.endpoint}'
        xyz = self._session.get(url=jive_ass_foo, params=instance.params).json()
        return xyz

    def __set__(self, instance, value):
        self.response = instance

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    def __setattr__(self, attr, value):
        super().__setattr__(attr, value)


class GlassnodeClient(GlassnodeBroker):
    """ TODO Create mongoDB handler for writes """
    response = GlassnodeBroker()
    _API_KEY = os.getenv('GLASSNODE')
    _load_endpoints = 'just/endpoints'
    _helper_endpoint = 'endpoints'
    _non_standard_responses = (
        'futures_funding_rate_perpetual_all',
        'futures_volume_daily_sum_all',
        'futures_volume_daily_perpetual_sum_all',
        'futures_open_interest_sum_all',
        'futures_open_interest_perpetual_sum_all',
        'futures_open_interest_latest',
        'futures_volume_daily_latest',
        'balance_exchanges_all',
        'balance_miners_all',
        'supply_distribution_relative',
        'exchanges_sum',
        'exchanges_relative',
        'exchanges_mean',
        'hash_ribbon',
        'difficulty_ribbon',
        'spent_output_price_distribution_ath',
        'spent_output_price_distribution_percent',
        'cyd',
        'cyd_supply_adjusted',
        'cyd_account_based_supply_adjusted',
        'cyd_account_based', 'cdd90_age_adjusted',
        'cdd90_account_based_age_adjusted',
        'stock_to_flow_ratio',
        'utxo_realized_price_distribution_ath',
        'utxo_realized_price_distribution_percent',
        'soab',
        'price_usd_ohlc',
        'liquid_illiquid_sum',
        'hodl_waves',
        'rcap_hodl_waves',
        'lth_sth_profit_loss_relative',
        'transfers_volume_miners_to_exchanges_all',
        'supply_distribution_relative'
    )

    def __init__(self, response=None, endpoint: str = None, **kwargs):
        super().__init__()
        self.known = self._file_reader()
        self.params = self._format_params(**kwargs)
        self.endpoint = endpoint
        self.response = response
        self.safe_ends = defaultdict(dict)

    def __repr__(self):
        return f'{self.response}'

    @staticmethod
    def _format_params(api_key=_API_KEY, **kwargs):
        par_dik = {key: val for key, val in kwargs.items()}
        par_dik.update({'api_key': api_key})
        print(f'parameters: {par_dik}')
        return par_dik

    @staticmethod
    def _the_validator(handler: str) -> str:
        """ Formats valid file path names passed from _file_writer/_file_reader """
        return ''.join(['_' if x in '/' else x for x in handler]).upper()

    def _update_endpoints(self):
        self.endpoint = self._helper_endpoint
        self._file_writer(self._dump_endpoints)

    def _file_reader(self, file_handler: str = _load_endpoints):
        _valid_name = self._the_validator(file_handler)
        logging.debug(f'>>> Reads:[ <{_valid_name}> ]')
        try:
            with open(file=f'get_glassnodes/{_valid_name}.txt', mode='r') as quick_reads:
                return json.loads(quick_reads.read())
        except Exception as e:
            raise e

    def _file_writer(self, func):
        _valid_name = self._the_validator(self.endpoint)
        logging.debug(f'>>> Writes:[ <{_valid_name}> ]')
        try:
            # with open(file=f'get_glassnodes/{_valid_name}.txt', mode='w+') as quick_write:
            #     dumped = json.dumps(func())
            #     assert dumped is (not {}) or (not None), 'you fucking donkey'
            #     quick_write.writelines(dumped)
            print('\n>>> JIVE ASS FOOL. . .')
        except Exception as e:
            raise e

    def _dump_endpoints(self):
        """ JSON.dumps """
        return json.dumps({'/'.join([e for e in elem['path'].split('/')][3:]): {
            'tier': elem['tier'], 'assets': elem['assets']} for elem in self.response})

    def _dump_standard(self):
        print(self.response)
        return None

    def _dump_non_standard(self):
        print(self.response)
        return None

    def _the_standard(self):
        if self.endpoint in self._helper_endpoint:
            print('>>> _the_standard: self.endpoint in self._helper_endpoint')
            return self._dump_endpoints
        elif self.endpoint not in self._non_standard_responses:
            print('>>> _the_standard: self.endpoint not in self._non_standard_responses ')
            return self._dump_standard
        else:
            print('>>> _the_standard: self.endpoint in self._')
            return self._dump_non_standard

    def _avaliable_endpoints(self, func, full=False):
        assert self.known is not None, 'you fucking donkey'
        if full:
            return self._file_reader(func)
        else:
            return self._file_reader(func)

    def _verbose_endpoints(self, endpt: str = None):
        self._verbose_endpoints(endpt=endpt)
        return {elem['symbol']: [elem['name'], elem['tags']]
                for elem in self.safe_ends[endpt]['assets']}

    def _query_endpoints(self, full: bool = True):
        """ Endpoint required, optional asset name for single asset inspection  """
        self.safe_ends = self._avaliable_endpoints(func=self._helper_endpoint, full=full)

    def _query_glassnode(self, endpoint: str, **kwargs):
        logging.debug(f'>>> _get_query({endpoint}, {kwargs})')
        self.endpoint = endpoint
        self.params = self._format_params(**kwargs)

    def file_reader(self, file_handler: str):
        """ Pass metric endpoint reads from disk, ex:'metrics/endpoint' """
        return self._file_reader(file_handler)

    def file_writer(self):
        """ Different writeFormat for [endpoints] vs [data] responses """
        self._file_writer(self._the_standard())


class Glassnodes(GlassnodeClient):
    def __init__(self, endpoint=None, **kwargs):
        super().__init__(endpoint=endpoint, **kwargs)

    def update_endpoints(self):
        """ Updates complete endpoint offered dictionary """
        self._update_endpoints()

    def verbose_endpoints(self, endpt: str = None, asset: str = None):
        """ Query a single endpoint and its optional parameters """
        self._query_endpoints(full=True)
        if not endpt:
            return self._verbose_endpoints()
        elif asset:
            return self._versbose_endpoints()[asset]
        else:
            return {endpt: self.safe_ends[endpt]}

    def quick_endpoints(self, show=False):
        """ Return dict of all avaliable endpoint paths {'super': 'sub'} """
        if show:
            pprint(self.known)
        return self.known

    def query_glassnode(self, endpoint: str, **kwargs):
        """
        Call 'metrics/endpoints/<sym> for available params for a given endpoint
        ONLY 'a' is REQUIRED for standard request queries

        * "a": str = 'asset_symbol',
        * "s": int = unix_timestamp,
        * "u": int = unix_timestamp,
        * "i": str = freq_interval(['1h', '24h', '10m', '1w', '1month']),
        * "f": str = format(['JSON', 'CSV']),
        * "c": str = currency(['NATIVE', 'USD'])
        * "e": str = 'exchange_name',
        * "timestamp_format": str = 'unix'.try('humanized(RFC-3339)'),
        * "api_key": autofill
        """
        self._query_glassnode(endpoint, **kwargs)
        return self.response


def format_wizard():
    # getting = GlassnodeClient()
    # return getting.query_glassnode(endpoint='addresses/count', a='BTC', i='24h')
    foo = Glassnodes()
    print(foo.quick_endpoints().keys())


if __name__ == '__main__':
    format_wizard()

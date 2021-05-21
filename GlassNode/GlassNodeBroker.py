import os
import logging
import pandas
from collections import defaultdict
from datetime import datetime
from typing import Optional, Dict, Any
from requests import Request, Session, Response
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s')


class GlassBroker:
    # TODO Make default params dict
    _GLASSNODE = "https://api.glassnode.com/v1/metrics"
    _HELPER = "https://api.glassnode.com/v2/metrics/endpoints"
    _API_KEY = os.getenv('GLASSNODE')

    def __init__(self):
        self._session = Session()

    @staticmethod
    def _process_response(path_index, asset, response: Response):
        logging.debug(f'<Response[ {response.status_code} : {response.reason} ]>\n')
        assert response is not None or {}, 'silly window guy'
        print(f'>>> pro_resp-path-index: {path_index}')
        return {path_index: [asset, response.json()]}

    def _request(self, request_method: str, abs_path: str, params: Optional[Dict[str, Any]] = None):
        params = {ki: vi for ki, vi in params.items() if vi is not None}
        params['api_key'] = self._API_KEY
        logging.debug(f"* params: {params}\n")
        response = self._session.send(
            Request(method=request_method, url=abs_path, params=params).prepare())
        response.close()
        return self._process_response('/'.join(abs_path.split('/')[-1:]), params['a'], response)

    def _get_request(self, path: str, root=_GLASSNODE, **kwargs) -> Any:
        """ Request handler """
        return self._request('GET', abs_path=root + path, params=kwargs)

    def get_metrics(self, index: str, endpoint: str, **kwargs):
        """ Query a specific metric from GlassnodeAPI"""
        assert index and endpoint is not None, 'Need API path you fucking donkey'
        return self._get_request(path=f'/{index}/{endpoint}', **kwargs)

    def get_all_endpoints(self) -> Any:
        """ Returns all available GlassnodeAPI endpoints """
        _helper = self._request('GET', abs_path=self._HELPER, params={'a': 'REF'})
        return _helper['endpoints'][1]

    def endpoint_helper(self, path=True, tier=True, assets=False, symbol=False, name=False, tags=False):
        locals_copy = locals().copy()
        _foo = [i for i in filter(lambda x: x not in 'self', locals_copy)
                if locals_copy[i] is not False]
        for results in self.get_all_endpoints():
            print([results[irx] if irx not in 'path' else
                   '/'.join(results[irx].split('/')[-2:]) for irx in _foo])


class GlassClient(GlassBroker):
    _PATH = ['index', 'endpoint']
    _PARAMS = ['a', 's', 'u', 'i', 'f', 'c', 'e', 'timestamp_format']

    def __init__(self, index=None, endpoint=None, asset='BTC',
                 start_point=None, until_point=None, interval='24h',
                 response_format='JSON', currency=None,
                 exchange_name=None, timestamp_format=None):
        super(GlassClient, self).__init__()
        self.index = index
        self.endpoint = endpoint
        self.a = asset
        self.s = start_point
        self.u = until_point
        self.i = interval
        self.f = response_format
        self.c = currency
        self.e = exchange_name
        self.timestamp_format = timestamp_format

    def _set_reusable(self, **kwargs):
        """ Set reusables worker method """
        for key, val in kwargs.items():
            if key in 'kwargs':
                for sub_key, sub_val in val.items():
                    setattr(self, sub_key, sub_val)
            setattr(self, key, val)

    def _get_reusables(self, ix: str = 'index', ep: str = 'endpoint'):
        """ Returns all class attributes that are not None """
        return (getattr(self, ix), getattr(self, ep),
                {k: v for k, v in {i: getattr(self, i) for i in self._PARAMS}.items() if v is not None})

    def glass_quest(self, index: str, endpoint: str, **kwargs):
        """
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
        self._set_reusable(**{k: v for k, v in locals().items() if k not in 'self'})
        _path, _ep, _kwargs = self._get_reusables()
        return self.get_metrics(index=_path, endpoint=_ep, **_kwargs)


class PandasWorker(GlassClient):
    def __init__(self, df: pandas.DataFrame = None):
        super(PandasWorker, self).__init__()
        self.df = df

    def json_to_pandas(self, index: str, endpoint: str, **kwargs):
        make_pandas = self.glass_quest(index=index, endpoint=endpoint, **kwargs)[endpoint][1]
        temp = defaultdict(list)
        for sets in make_pandas:
            key, val = sets.items()
            if key in temp:
                temp[key] = [val]
            else:
                temp[key].append(val)

        print(temp)


def standard_response(foobar):
    """ For use with responseType = {'t': int, 'v': int} """
    if input('Show? ') not in 'n':
        for feeds, respo in foobar.items():
            _chan, _asses = feeds.upper(), respo[0]
            for elem in respo[1]:
                _ts, _data = datetime.utcfromtimestamp(elem['t']), elem['v']
                print(f"* {_asses}_{_chan} * [ <{_ts}> : <{_data}> ]")


if __name__ == '__main__':
    print(f'\n>>> Initialized TheApeSlayer as {__name__}\n')
    # gg = GlassClient()
    # result = gg.glass_quest(index='blockchain', endpoint='block_height')

    pandy = PandasWorker()
    pandy.json_to_pandas(index='blockchain', endpoint='block_height')

    # standard_response(result)

    # gg.endpoint_helper()
    # result = gg.glass_quest(index='blockchain', endpoint='block_height')  #, a='ETH', i='1w')


# class MongoBroker:
#     def __init__(self):
#         pass
#
#
# class MongoClient(MongoBroker):
#     def __init__(self):
#         super(MongoClient, self).__init__()

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

from ConfigureHelper import *
from pprint import pprint


class TopsREST(RESTapi):
    """
    Wrapper for easy access to all the WebSocket helper endpoints
    TODO Add descriptor methods?
    TODO 'Push-to-Mongo' method for concurrent DB transaction
    """
    
    rest = RESTapi()
    
    def __init__(self):
        super().__init__()
        
    def tops_param_dict(self, limit=10, page=0, fiat='USD', asset_class='ALL'):
        """
        Parameters dictionary passed to 'params' keyword argument in requests.get()
        Attributes: limit, page, tsym, assetClass, ascending, sign
        """
        self.limit = limit
        self.page = page
        self.tsym = fiat
        self.asset_class = asset_class
        self.param_dict = dict(limit=self.limit, page=self.page, tsym=self.tsym, asset_class=self.asset_class)
    
    def top_vol_subs(self, **kwargs):
        """
        Get a number of top coins by their total volume across all markets in the last 24 hours.
        Default value is first page (0) and the top 10 coins.
        Attributes: limit, page, tsym, assetClass, ascending, sign
        """
        self.endpoint = self.root_endpoint + self.vol_subs_24h
        self.tops_param_dict(**kwargs)
        self.requester()
        return self.get_json()
        
    def top_tier_vol(self, **kwargs):
        """
        Get a number of top coins by their total top tier volume on the top 20 markets in the last 24 hours.
        Default value is first page (0) and the top 10 coins.
        Attributes: limit, page, tsym, assetClass, ascending, sign
        """
        self.endpoint = self.root_endpoint + self.top_tier_vol_subs_24hr
        self.tops_param_dict(**kwargs)
        self.requester()
        return self.get_json()
        
    def top_mrkt_cap_subs(self, **kwargs):
        """
        Get a number of top coins by their market cap.
        Default value is first page (0) and the top 10 coins.
        Attributes: limit, page, tsym, assetClass, ascending, sign
        """
        self.endpoint = self.root_endpoint + self.market_cap_subs
        self.tops_param_dict(**kwargs)
        self.requester()
        return self.get_json()
    
    def top_direct_vol(self, **kwargs):
        """
        Get a number of top coins by their total top tier volume on the top 20 markets in the last 24 hours.
        Default value is first page (0) and the top 10 coins.
        Attributes: limit, page, tsym, assetClass, ascending, sign
        """
        self.endpoint = self.root_endpoint + self.direct_vol
        self.tops_param_dict(**kwargs)
        self.requester()
        return self.get_json()
        
    def top_by_price(self, **kwargs):
        """
        Get a number of top coins by their price.
        Default value is first page (0) and the top 10 coins.
        """
        self.endpoint = self.root_endpoint + self.by_price
        self.tops_param_dict(**kwargs)
        self.requester()
        return self.get_json()
        
    def top_percent_change(self, **kwargs):
        """
        Get a number of top coins by their price percentage change in the last 24 hours.
        Default value is first page (0) and the top 10 coins.
        """
        self.endpoint = self.root_endpoint + self.percent_change
        self.tops_param_dict(**kwargs)
        self.requester()
        return self.get_json()
    
    def __repr__(self):
        return f'{self.param_dict}'


class SubCallREST(RESTapi):
    """ Request information about stream subscriptions. Check method docstrings for specifics """
    
    rest = RESTapi()
    
    def __init__(self):
        super().__init__()
        
    def subs_pair(self, fsym='BTC', tsym='USD'):
        """
        Get fsym info, agg streaming snapshot,
        and all the available streamer subscription channels for the requested pairs.
        """
        self.endpoint = self.root_endpoint + self.subs_by_pair
        self.fsyms = fsym
        self.tsym = tsym
        self.param_dict = dict(fsym=self.fsyms, tsyms=self.tsym)
        self.requester()
        return self.get_json()

    def sub_watchlist(self, fsyms='BTC', tsym='USD'):
        """
        Get combinations of subs and pricing info in order
        to know what needs to be streamed and how to connect to the streamers.
        For response conversion formatting visit link below:
        https://min-api.cryptocompare.com/documentation/websockets?key=Streaming&cat=coinsGeneralInfoEndpoint
        """
        self.endpoint = self.endpoint + self.subs_watchlist
        self.fsyms = fsyms
        self.tsym = tsym
        self.param_dict = dict(fsyms=self.fsyms, tsym=self.tsym)
        self.requester()
        return self.get_json()

    def general_coin_info(self, fsyms='BTC,ETH', tsym='USD'):
        """
        Get combinations of subs and pricing info in order
        to know what needs to be streamed and how to connect to the streamers.
        """
        self.endpoint = "https://min-api.cryptocompare.com/data/coin/generalinfo"
        self.fsyms = fsyms
        self.tsym = tsym
        self.param_dict = dict(fsyms=fsyms, tsym=tsym)
        self.requester()
        return self.get_json()
    

def telesto(sets=True, genfo=False):
    """
    Call function with no arguments
    Displays All helper endpoints with default arguments
    TODO Add JSON.dump() 'pretty_format' method for human readability
    """
    
    def top_streams(**kwargs):
        """ :return: Dictionary of ALL-TOP helper endpoint JSON response objects """
        tops = TopsREST()
        return {"Top_TotalVolume": tops.top_vol_subs(**kwargs),
                "Top_PercentChange": tops.top_percent_change(**kwargs),
                "Top_MarketCap": tops.top_mrkt_cap_subs(**kwargs),
                "Top_DirectVolume": tops.top_direct_vol(**kwargs)}

    def gen_info(**kwargs):
        """
        TODO Response formatting
        Prints JSON responses for: subscription pairs, subscription watch lists, and general coin info
        :param kwargs: fsym='BTC' -> Crypto Currency
        :param kwargs: tsym='USD' -> Conversion Currency
        :return: Dictionary of ALL-SUBS helper endpoints
        """
        subs = SubCallREST()
        return {"Sub_Pair": subs.subs_pair(**kwargs),
                "Sub_Watchlist": subs.sub_watchlist(**kwargs),
                "Gen_CoinInfo": subs.general_coin_info(**kwargs)}
        
    if sets and genfo:
        return top_streams, gen_info
    elif genfo and not sets:
        return gen_info
    else:
        return top_streams


def nested_printer(responses):
    dik = dict()
    for request_type, response in responses.items():
        dik[request_type] = [data['CoinInfo']['Name'] for data in response['Data']]
    return dik

        
if __name__ == "__main__":
    print(f'\nHelperEndPoints Initializing as {__name__}\n')

else:
    print(f'\nHelperEndPoints Initializing as {__name__}\n')

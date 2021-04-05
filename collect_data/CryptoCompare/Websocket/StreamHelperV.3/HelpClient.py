from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
apiKey = os.getenv('CCOMPARE_DATA_API_KEY')


class PrepareRequest(object):
    def __init__(self):
        self.__endpoint = None
        self.__limit = None
        self.__page = None
        self.__tsym = None
        self.__asset_class = None
        self.__parameters = None
    
    @property
    def endpoint(self):
        """ REST API endpoint, key="Full-URL-Path" listed in InitRequestParams, default='Top_Percent_Change' """
        return self.__endpoint
    
    @property
    def limit(self):
        """ Number of CryptoAssets to return, default=10 """
        return self.__limit
    
    @property
    def page(self):
        """ TODO wtf are pagination requests, default='0' """
        return self.__page
    
    @property
    def tsym(self):
        """ The fiat conversion currency, default='USD' """
        return self.__tsym
    
    @property
    def asset_class(self):
        """ TODO Check CryptoCompare and fill what this does, default='ALL' """
        return self.__asset_class
    
    @property
    def parameters(self):
        """ Parameters appended to 'endpointURL' through requests.get(params=parameters) """
        return self.__parameters
    
    @endpoint.setter
    def endpoint(self, value):
        self.__endpoint = value

    @limit.setter
    def limit(self, value):
        self.__limit = value

    @page.setter
    def page(self, value):
        self.__page = value

    @tsym.setter
    def tsym(self, value):
        self.__tsym = value

    @asset_class.setter
    def asset_class(self, value):
        self.__asset_class = value
    
    @parameters.setter
    def parameters(self, value):
        self.__parameters = value


class InitRequestParams(PrepareRequest):
    
    def __init__(self):
        super(InitRequestParams, self).__init__()
        self.prepping = PrepareRequest()
        self.url = str()
        self.endings = {
            "Top_Vol_Subs": 'https://min-api.cryptocompare.com/data/top/totalvol',
            "Top_Tier_VolSubs": 'https://min-api.cryptocompare.com/data/top/totaltoptiervol',
            "Top_Mkt_Cap": 'https://min-api.cryptocompare.com/data/top/mktcap',
            "Top_Direct_Vol": 'https://min-api.cryptocompare.com/data/top/directvol',
            "Top_By_Price": 'https://min-api.cryptocompare.com/data/top/price',
            "Top_Percent_Change": 'https://min-api.cryptocompare.com/data/top/percent'}
    
    def set_url(self, url="Top_Percent_Change"):
        self.url = self.endings[url]
    
    def setting_parameters(self):
        self.parameters = dict(limit=self.limit,
                               page=self.page,
                               tsym=self.tsym,
                               asset_class=self.asset_class,
                               api_key=apiKey)
        
    def set_parameters(self, limit=10, page=0, fiat='USD', asset_class='ALL'):
        self.limit = limit
        self.page = page
        self.tsym = fiat
        self.asset_class = asset_class
        self.setting_parameters()
    
    def __repr__(self):
        return f'{self.url, self.parameters}'


def verifier(vary):
    """ Called automatically from rest_caller to verify user list elements """
    verified = ["Top_Percent_Change", "Top_Vol_Subs", "Top_Mkt_Cap",
                "Top_By_Price", "Top_Direct_Vol", "Top_Tier_Vol_Subs"]

    def inner_verifier(unverified):
        vary()
        if unverified not in verified:
            return False
        else:
            pass
        return True
    return inner_verifier


def rest_caller(resting):
    """ Wrapper for 'ParameterMaker' tasks """
    maker = InitRequestParams()
    prepped = dict()

    def inner_rest(metrics, **kwargs):
        """
        Generates dictionary of preset inputs to use with repetitive request.get() calls
        Iterates through metrics list verifying user input is correct with @verifier decorator
        :param metrics: list of valid endpoints as mentioned in 'user_entry' docstring
        :param kwargs: valid parameter keywords as mentioned in 'helper_client' docstring
        :return: prepped_dictionary: {'metric_name': {'url': request.url, 'parameters': request.params}}
        """
        resting()
        for item in metrics:
            if not user_entry(item):
                break
            else:
                maker.set_url(item)
                maker.set_parameters(**kwargs)
                prepped[item] = {'url': maker.url, 'parameters': maker.parameters}
        return prepped
    return inner_rest


@verifier
def user_entry():
    """
    Verifies user entry is a valid REST-api endpoint
    Valid Endpoints:
        >> [Top_Vol_Subs, Top_Tier_VolSubs, Top_Mkt_Cap, Top_Direct_Vol, Top_By_Price, Top_Percent_Change]
    """
    pass


@rest_caller
def helper_client():
    """
    TODO implement keyword argument hinting for decorators and wtf is pagination
    Decorator to initiate class instance of InitRequestParams
    Decorator used by CallerClient.call_rest() method
    :param: url: is the desired helper endpoint
    :param: limit: number of coins to return
    :param: page: pagination: check CryptoCompare API details
    :param: fiat: 'is tsym', (i.e. - base conversion currency)
    :param: asset_class: check CryptoCompare API details
    :returns: prepped_dictionary: {'metric_name': {'url': request.url, 'parameters': request.params}}
    """
    pass


if __name__ == "__main__":
    from pprint import pprint
    # import logging as logs
    # logs.basicConfig(filename='dataQuickCheck.log', filemode='w', level=logs.INFO)
    print(f"\n>>> Initializing `HelpClient` as '{__name__}'...")
    helpers = ["Top_By_Price", "Top_Mkt_Cap", "Top_Vol_Subs", "Top_Direct_Vol"]
    foo = helper_client(helpers, limit=40, fiat='USD')
    pprint(foo, indent=4)

else:
    print(f"\n>>> Initializing `HelpClient` as '{__name__}'...")
    InitialHelper = helper_client

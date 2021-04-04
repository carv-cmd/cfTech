from dotenv import load_dotenv, find_dotenv
import os
# import requests
# from datetime import datetime
# import time
from pprint import pprint

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
        print('ENDPOINT PROPERTY')
        return self.__endpoint
    
    @property
    def limit(self):
        print('LIMIT PROPERTY')
        return self.__limit
    
    @property
    def page(self):
        print('PAGE PROPERTY')
        return self.__page
    
    @property
    def tsym(self):
        print('TSYM PROPERTY')
        return self.__tsym
    
    @property
    def asset_class(self):
        print('ASSET_CLASS PROPERTY')
        return self.__asset_class
    
    @property
    def parameters(self):
        return self.__parameters
    
    @endpoint.setter
    def endpoint(self, value):
        print(f'>> CALLED: @endpoint.setter')
        self.__endpoint = value

    @limit.setter
    def limit(self, value):
        print(f'>> CALLED: @limit.setter')
        self.__limit = value

    @page.setter
    def page(self, value):
        print(f'>> CALLED: @page.setter')
        self.__page = value

    @tsym.setter
    def tsym(self, value):
        print(f'>> CALLED: @tsym.setter')
        self.__tsym = value

    @asset_class.setter
    def asset_class(self, value):
        print(f'>> CALLED: @asset_class.setter')
        self.__asset_class = value
    
    @parameters.setter
    def parameters(self, value):
        self.__parameters = value


class InitializeRequest(PrepareRequest):
    
    def __init__(self):
        super(InitializeRequest, self).__init__()
        self.prepping = PrepareRequest()
        self.url = str()
        self.endings = {
            "Top_Vol_Subs": 'https://min-api.cryptocompare.com/data/top/totalvol',
            "Top_Tier_VolSubs": 'https://min-api.cryptocompare.com/data/top/totaltoptiervol',
            "Top_Mkt_Cap": 'https://min-api.cryptocompare.com/data/top/mktcap',
            "Top_Direct_Vol": 'https://min-api.cryptocompare.com/data/top/directvol',
            "Top_By_Price": 'https://min-api.cryptocompare.com/data/top/price',
            "Top_Percent_Change": 'https://min-api.cryptocompare.com/data/top/percent'}
        
    def setting_parameters(self):
        self.parameters = dict(limit=self.limit,
                               page=self.page,
                               tsym=self.tsym,
                               asset_class=self.asset_class)
        
    def set_url(self, url="Top_Percent_Change"):
        print(f'\t>> INSTANCE.METHOD: set_url')
        self.url = self.endings[url]

    def set_parameters(self, limit=10, page=0, fiat='USD', asset_class='ALL'):
        print(f'\t>> INSTANCE.METHOD: set_parameters')
        self.limit = limit
        self.page = page
        self.tsym = fiat
        self.asset_class = asset_class
        self.setting_parameters()
        
    def __str__(self):
        return self.url


def verifier(vary):
    verified = ["Top_Percent_Change", "Top_Vol_Subs", "Top_Mkt_Cap",
                "Top_By_Price", "Top_Direct_Vol", "Top_Tier_Vol_Subs"]

    def verifying(unverified):
        vary()
        if unverified not in verified:
            print(f"\n\t>>> INVALID INPUT: ['{unverified}']")
            return False
        else:
            pass
        return True
    return verifying


def rest_caller(resting):
    maker = InitializeRequest()
    prepped = dict()
    
    def inner_wrapper(metrics, **kwargs):
        resting()
        for item in metrics:
            print(item)
            if not user_entry(item):
                break
            else:
                maker.set_url(item)
                maker.set_parameters(**kwargs)
                prepped[item] = {'url': maker.url, 'parameters': maker.parameters}
                print(f'\n>> {item} && {maker.parameters} '
                      f'\n>>> FAILED SUCCESSFULLY\n')
        return prepped
    return inner_wrapper


@verifier
def user_entry():
    pass


@rest_caller
def helper_client():
    pass


if __name__ == "__main__":
    print(f"\n>>> Initializing `HelpClient` as '{__name__}'...\n")
    helpers = ["Top_By_Price", "Top_Mkt_Cap", "Top_Vol_Subs", "Top_Direct_Vol"]
    foo = helper_client(helpers, limit=40)
    pprint(foo, indent=4)

else:
    print(f"\n>>> Initializing `HelpClient` as '{__name__}'...\n")
    HelperEndpoints = helper_client

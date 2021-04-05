from HelpClient import *
import requests
from datetime import datetime
import time


class StartClient(object):
    def __init__(self):
        self.__helper = None
        self.daters = dict()

    @property
    def helper(self):
        return self.__helper

    @helper.setter
    def helper(self, value):
        self.__helper = value

    def __setattr__(self, key, value):
        super(StartClient, self).__setattr__(key, value)
        

class CallerClient(StartClient):
    def __init__(self):
        super(CallerClient, self).__init__()
    
    def call_rest(self):
        for ki, val in self.helper.items():
            print(f"\n\t>>> CALLING REST:FROM:[{ki}]")
            self.daters[ki] = requests.get(val['url'], params=val['parameters']).json()
            del self.daters[ki]['SponsoredData']
            time.sleep(.25)

    def set_helper(self, enders, **kwargs):
        self.helper = InitialHelper(enders, **kwargs)
        self.call_rest()


if __name__ == "__main__":
    print(f"\n>>> Initializing `RESTClient` as '{__name__}'...")
    
    helpers = ["Top_By_Price", "Top_Mkt_Cap", "Top_Vol_Subs", "Top_Direct_Vol"]
    cc = CallerClient()
    cc.set_helper(helpers, limit=10, fiat='USD')
    
    pprint(cc.daters)

else:
    print(f"\n>>> Initializing `RESTClient` as '{__name__}'...")

import requests
from datetime import datetime
import time
from HelpClient import InitialHelper


class StartClient(object):
    def __init__(self):
        self.__helper = None
        self.daters = dict()
    
    def __setattr__(self, key, value):
        super(StartClient, self).__setattr__(key, value)

    @property
    def helper(self):
        return self.__helper

    @helper.setter
    def helper(self, value):
        self.__helper = value
        

class CallerClient(StartClient):
    def __init__(self):
        super(CallerClient, self).__init__()
    
    def auto_rest(self):
        for ki, val in self.helper.items():
            ts = datetime.now().isoformat()
            print(f"\n\t>>> CALLING REST:FROM:[{ki}]")
            self.daters[ki + ts] = requests.get(val['url'], params=val['parameters']).json()
            del self.daters[ki]['SponsoredData']
            time.sleep(.25)

    def set_help(self, enders, **kwargs):
        self.helper = InitialHelper(enders, **kwargs)
        self.auto_rest()


# instance.daters[ki]['Data']
if __name__ == "__main__":
    from pprint import pprint
    print(f">>> Initializing `RESTClient` as '{__name__}'...")
    helpers = ['Top_Percent_Change']  # "Top_By_Price", "Top_Mkt_Cap", "Top_Vol_Subs", "Top_Direct_Vol"]
    cc = CallerClient()
    cc.set_help(helpers, limit=10, fiat='USD')
    pprint(cc.daters)

else:
    print(f">>> Initializing `RESTClient` as '{__name__}'...")
    Rested = CallerClient()

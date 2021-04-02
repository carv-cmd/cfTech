# from pymongo import MongoClient as Mcl
from dotenv import load_dotenv, find_dotenv
import os
import requests
import time
from HelperTasks import *
from pprint import pprint
# import logging as logs

# logs.basicConfig(filename='dataQuickCheck.log', filemode='w', level=logs.INFO)

line = '\n' \
       '--------------------------------------------------------------------------' \
       '\n'
load_dotenv(find_dotenv())
apiKey = os.getenv('CCOMPARE_DATA_API_KEY')


class PrepareRequest(dict):
    """
    Descriptor class for CryptoCompare REST-helper-endpoints wrapper
    Initiates the parameter dictionary with all necessary default values
    """
    
    def __init__(self, limit=10, page=0, fiat='USD', asset_class='ALL'):
        super(PrepareRequest, self).__init__()
        self.requestData = dict(limit=limit, page=page, tsym=fiat, asset_class=asset_class, api_key=apiKey)
    
    def __setattr__(self, key, value):
        print(f">> Setting.PrepareRequest({key}). . .")
        super().__setattr__(key, value)


class TopLists:
    """ Set endpoint url for class instance """
    top_ends = {
            "TopVolSubs": 'https://min-api.cryptocompare.com/data/top/totalvol',
            "TopTierVolSubs": 'https://min-api.cryptocompare.com/data/top/totaltoptiervol',
            "TopMktCap": 'https://min-api.cryptocompare.com/data/top/mktcap',
            "TopDirectVol": 'https://min-api.cryptocompare.com/data/top/directvol',
            "TopByPrice": 'https://min-api.cryptocompare.com/data/top/price',
            "TopPercentChange": 'https://min-api.cryptocompare.com/data/top/percent'
    }
    
    def __init__(self, endpoint='TopPercentChange', **kwargs):
        self.url = self.top_ends[endpoint]
        self.parameters = vars(PrepareRequest(**kwargs))
    
    def __getitem__(self, item):
        print(f">> Getting.TopLists({item}). . .")
        return self.__dict__[item]


class HaveFunStayingPoor:
    """ TODO Docstring functionality """
    
    @staticmethod
    def send_requests(metrics):
        """
        Wrapper to initiate the full request.get(helpers) task
        TODO Add full docstring for class methods
        """
        def response_object(**sendto):
            """
            TODO Docstring and mongo push
            TODO :MongoDB: dict(metric=report, data=requests.get(passing[0], params=passing[1]).json())
            """
            response_dict = dict()
            for report, passing in sendto.items():
                try:
                    daters = requests.get(passing[0], params=passing[1])
                    print(f'>>> Received Request Response:({report}):\n\tFrom: "{daters.url}"')
                    response_dict[report] = daters.json()
                    del response_dict[report]['SponsoredData']
                    time.sleep(.25)
                    
                except requests.exceptions.ConnectionError:
                    print('CONNECTION REFUSED INCREASE DURATION BETWEEN SUBSEQUENT REQUESTS')
                    break
                    
            return response_dict

        def sender(**kwargs):
            """
            TODO Docstring functionality
            """
            sendto = dict()
            for elem in metrics:
                foo = TopLists(endpoint=elem, **kwargs)
                sendto[elem] = [foo['url'], foo['parameters']['requestData']]
                print(f"\n>>> GENERATING METRICS FOR: {elem}. . .")

            print(line)
            return response_object(**sendto)
        return sender

    def send_agent(self, **kwargs):
        """
        Create a list named 'check_these' in the global name space containing the metrics to request
        Options: ["TopPercentChange", "TopVolSubs", "TopMktCap", "TopByPrice", "TopDirectVol", "TopTierVolSubs"]
        :param kwargs: limit=10, page=0, fiat='USD', asset_class='ALL'
        :return: dictionary object where; key='metric' & value='responseData_FullNames_list"
        TODO Generalize this docstring
        """
        get_from = self.send_requests(my_list)
        return_values = get_from(**kwargs)
        return return_values


def run_wrapper(func):
    def execute(check_these):
        func()
        if not Verifier(check_these):
            print("\nVerify List Entries. . .")
        
        else:
            cc = HaveFunStayingPoor()
            valuable_data = cc.send_agent(limit=10)  # returns full response
            
            coin_wizard = Printer(valuable_data)  # returns user sliced response
            print(line)
            pprint(coin_wizard)
            
    return execute
    

@run_wrapper
def execute_call():
    print('>>> EXECUTING REQUEST.GET(). . .')


if __name__ == "__main__":
    print(f"\n>>> Initializing `ConfigureHelperV.2` as '{__name__}'...\n")
    
    my_list = ["TopPercentChange", "TopMktCap"]
    execute_call(my_list)
    
else:
    print(f"\n>>> Initializing `ConfigureHelperV.2` as '{__name__}'...\n")
    check_list = []
    hfspClient = HaveFunStayingPoor

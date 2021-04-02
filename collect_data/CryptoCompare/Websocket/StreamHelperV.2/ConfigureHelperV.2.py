from pymongo import MongoClient as Mcl
from dotenv import load_dotenv, find_dotenv
import logging as logs
import os
import requests
import time
from pprint import pprint

line = '\n' \
       '--------------------------------------------------------------------------' \
       '\n'
load_dotenv(find_dotenv())
apiKey = os.getenv('CCOMPARE_DATA_API_KEY')
logs.basicConfig(filename='BSON_fileSize.log', filemode='w', level=logs.INFO)


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
        
    def __repr__(self):
        return f"{self.__dict__['requestData']}"
    

class TopLists:
    """ Set endpoint url for class instance """
    top_end = {
            "TopVolSubs": 'https://min-api.cryptocompare.com/data/top/totalvol',
            "TopTierVolSubs": 'https://min-api.cryptocompare.com/data/top/totaltoptiervol',
            "TopMktCap": 'https://min-api.cryptocompare.com/data/top/mktcap',
            "TopDirectVol": 'https://min-api.cryptocompare.com/data/top/directvol',
            "TopByPrice": 'https://min-api.cryptocompare.com/data/top/price',
            "TopPercentChange": 'https://min-api.cryptocompare.com/data/top/percent'
    }
    
    def __init__(self, endpoint='TopPercentChange', **kwargs):
        self.url = self.top_end[endpoint]
        self.parameters = vars(PrepareRequest(**kwargs))
    
    def __getitem__(self, item):
        print(f">> Getting.TopLists({item}). . .")
        return self.__dict__[item]
        
    def __repr__(self):
        return f'\nTargetURL: {self.url}\n' \
               f'\nRequestParameters: {self.parameters}\n'


class ReturnToSender(dict):
    def __init__(self):
        super(ReturnToSender, self).__init__()
    
    def send_requests(self, metrics):
        """ Wrapper to initiate the full request.get(helpers) sequence """
        
        def response_object(**sendto):
            response_dict = dict()
            for report, passing in sendto.items():
                try:
                    # TODO :MongoDB: dict(metric=report, data=requests.get(passing[0], params=passing[1]).json())
                    daters = requests.get(passing[0], params=passing[1])
                    print(f">>> Attempting Request:({report}):\n\tFrom: '{daters.url}'")
                    response_dict[report] = daters.json()
                    del response_dict[report]['SponsoredData']
                    time.sleep(.25)
                    
                except requests.exceptions.ConnectionError:
                    requests.status_codes = 'Connection refused'
                    print('CONNECTION REFUSED INCREASE DURATION BETWEEN SUBSEQUENT REQUESTS')
            print(line)
            pprint(response_dict)
            print(line)
            return response_dict
        
        def sender(**kwargs):
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
        """
        verified = ["TopPercentChange", "TopVolSubs", "TopMktCap",
                    "TopByPrice", "TopDirectVol", "TopTierVolSubs"]
        try:
            for checking in check_these:
                if checking in verified:
                    pass
                else:
                    raise ValueError

            get_from = self.send_requests(check_these)
            return_values = get_from(**kwargs)
            
            degens = dict()
            for ik, iv in return_values.items():
                degen_names = []
                degen_streams = []
                
                for metric in iv['Data']:
                    degen_names.append(metric['CoinInfo']['FullName'])
                    degen_streams.append(metric['CoinInfo']['SubsNeeded'])
                    
                degens[ik] = degen_names
    
            print('\n------>>> TASK FAILED SUCCESSFULLY <<<------')
            return degens
        
        except ValueError:
            print('Check Your Metrics-List Strings!!!')
            raise


if __name__ == "__main__":
    print(f"\n>>> Initializing `ConfigureHelperV.2` as '{__name__}'...\n")

    check_these = ["TopPercentChange"]
    cc = ReturnToSender()
    
    # KWARGS: send_agent(limit = 10, page = 0, fiat = 'USD', asset_class = 'ALL')
    for ikey, ivalue in cc.send_agent(limit=10).items():
        print(f"\n>>> Metric: {ikey} <<<"
              f"\n---------------------------------------"
              f"\n{ivalue}")
        
else:
    print(f"\n>>> Initializing `ConfigureHelperV.2` as '{__name__}'...\n")
    check_these = []
    RequestClient = ReturnToSender
    
# def to_bson(json_elem):
    #     bson_obj = bson.encode(json_elem)
    #     logs.info(f"\nAttempting Connection w/: {req_url}"
    #               f"\nMAX byte count for BSON document is (160,000,000bytes) or (16MB)!"
    #               f"\n\tCurrent BSON Representation Byte Count: ({len(bson_obj)}-rawBytes)"
    #               f"\n\t\tApprox Document Size:\n\t\t\t({len(bson_obj) / 1000000}MB / 16MB)\n"
    #               f"\n\n{bson_obj}\n\n")
    #     return bson_obj

comment_folder = None

# def send_requests(metrics):
#     """ Wrapper to initiate """
#     def response_object(**sendto):
#         response_dict = dict()
#
#         for report, passing in sendto.items():
#             try:
#                 # TODO :MongoDB: dict(metric=report, data=requests.get(passing[0], params=passing[1]).json())
#                 print(f">>> Attempting Request:({report}):\n\tFrom: '{passing[0]}'")
#                 daters = requests.get(passing[0], params=passing[1]).json()
#                 response_dict[report] = daters
#                 time.sleep(.25)
#             except requests.exceptions.ConnectionError:
#                 requests.status_codes = 'Connection refused'
#                 print('CONNECTION REFUSED INCREASE DURATION BETWEEN SUBSEQUENT REQUESTS')
#
#         del response_dict['TopPercentChange']['SponsoredData']
#         return response_dict
#
#     def sender(**kwargs):
#         sendto = dict()
#
#         for elem in metrics:
#             foo = TopLists(endpoint=elem, **kwargs)
#             sendto[elem] = [foo['url'], foo['parameters']['requestData']]
#             print(f"\n>>> GENERATING METRICS FOR: {elem}. . .")
#             pprint(sendto[elem])
#             print(line)
#
#         return response_object(**sendto)
#     return sender


# def send_agent(**kwargs):
#     """
#     Create a list named 'check_these' in the global name space containing the metrics to request
#     Options: ["TopPercentChange", "TopVolSubs", "TopMktCap", "TopByPrice", "TopDirectVol", "TopTierVolSubs"]
#     :param kwargs: limit=10, page=0, fiat='USD', asset_class='ALL'
#     :return: dictionary object where; key='metric' & value='responseData_FullNames_list"
#     """
#     get_from = send_requests(check_these)
#     return_values = get_from(**kwargs)
#     degens = dict()
#
#     for ik, iv in return_values.items():
#         deg = []
#         for metric in iv['Data']:
#             deg.append(metric['CoinInfo']['FullName'])
#         degens[ik] = deg
#
#     print('\n------>>> TASK FAILED SUCCESSFULLY <<<------\n')
#     return degens
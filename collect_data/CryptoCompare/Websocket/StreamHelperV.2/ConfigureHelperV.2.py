from dotenv import load_dotenv, find_dotenv
import logging as logs
import os
import requests
import bson

load_dotenv(find_dotenv())
apiKey = os.getenv('CCOMPARE_DATA_API_KEY')

logs.basicConfig(filename='BSON_fileSize.log', filemode='w', level=logs.INFO)


class PrepareRequest(dict):
    """ Descriptor class for CryptoCompare REST API calls """
    
    def __init__(self, limit=10, page=0, fiat='USD', asset_class='ALL'):
        super(PrepareRequest, self).__init__()
        self.requestData = dict(limit=limit, page=page, tsym=fiat, asset_class=asset_class, api_key=apiKey)
    
    def __setattr__(self, key, value):
        print(f">>> Setting '{key}'...")
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
        print(f">>> Getting '{item}'")
        return self.__dict__[item]
        
    def set_url(self, change_url):
        self.url = self.top_end[change_url]
        
    def __repr__(self):
        return f'\nTargetURL: {self.url}\n' \
               f'\nRequestParameters: {self.parameters}\n'


def send_wrapper():
    
    def send_requests(new_endpoint='TopPercentChange'):
        foobar = TopLists(limit=10)
        req_url = foobar['url']
        req_parameters = foobar['parameters']['requestData']
        
        def to_bson(json_elem):
            bson_obj = bson.encode(json_elem)
            logs.info(f"\nResponse From: {req_url}"
                      f"\nMAX byte count for BSON document is (160,000,000bytes) or (16MB)!"
                      f"\n\tCurrent BSON Representation Byte Count: ({len(bson_obj)}-rawBytes)"
                      f"\n\t\tApprox Document Size:\n\t\t\t({len(bson_obj) / 1000000}MB / 16MB)\n"
                      f"\n\n{bson_obj}\n\n")
            return bson_obj
        
        def response_object():
            foobar.set_url(new_endpoint)
            try:
                return to_bson(requests.get(req_url, params=req_parameters).json())
            except TypeError or KeyError or ValueError:
                raise
    
        return response_object()
    
    return send_requests
    

if __name__ == "__main__":
    print(f"\n>>> Initializing `ConfigureHelperV.2` as '{__name__}'...\n")
    
    try:
        check_all = ["TopVolSubs", "TopTierVolSubs", "TopMktCap", "TopDirectVol", "TopByPrice", "TopPercentChange"]
        sender = send_wrapper()
        for metric in check_all:
            sender(metric)
        print('\nTask Completed Successfully!\nCheck .log for response size.\n')
        
    except TypeError or KeyError or ValueError:
        print('FIX REQUEST METHOD')
        raise

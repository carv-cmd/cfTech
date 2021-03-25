import os
import requests
import datetime
from dotenv import load_dotenv, find_dotenv
from call_threader import *

load_dotenv(find_dotenv())
apikey = os.getenv("CCOMPARE_DATA_API_KEY")


def persist_call():
    try:
        payload = {"fsym": 'BTC', "tsyms": 'USD', "api_key": apikey}
        req = requests.get("https://min-api.cryptocompare.com/data/price", params=payload)
        temp = req.json()
        key = f"{datetime.datetime.now()}"

        data_points[key] = temp[payload['tsyms']]
        print(f'\n{key} = ${data_points[key]}')
    except KeyError or ConnectionRefusedError or ConnectionError:
        print("LENGTHEN REQUEST INTERVAL")


print(f"\nInitializing Persistent Channel...")

if __name__ == "__main__":

    data_points = {"Currency": 'BTC-USD'}

    @set_interval(0.5)
    def foo():
        persist_call()

    stopper = foo()

    time.sleep(360)
    stopper.set()

    print(data_points)


else:
    print(f"\nCalled Module: {__name__}\n"
          f"\nInitializing Persistent Channel")

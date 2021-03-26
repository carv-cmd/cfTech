# import os
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from pprint import pprint
# from dotenv import load_dotenv, find_dotenv
import pandas as pd
from pprint import pprint

df = pd.read_json('NVDA_tickData.json')

pprint(df)

#
# load_dotenv(find_dotenv())
# reset = os.getcwd()
#
# dir_key = os.getenv('BTC_DATA')[2:-1]
#
# print()
# print(dir_key)
# print(type(dir_key))
#
# os.chdir(r"{}".format(dir_key))
# print('Changed')
# print('resetting')
# os.chdir(reset)

# f = open('BTC_Daily_OHLCV')
# print(f'\n{f.readline()}\n{f.readline()}\n{f.readline()}')
# f.close()


# daters = pd.read_csv('BTC_Daily_OHLCV', nrows=100)

# pprint(daters)


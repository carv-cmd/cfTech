import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import pandas_datareader.data as web

load_dotenv(find_dotenv())
alpha_key = os.environ.get("ALPHAVANTAGE_API_KEY")
print(f'\nALPHAVANTAGE_API_KEY={alpha_key}\n')

# foo = web.DataReader('GLXY', 'av-daily', start=datetime(2020, 2, 9),
#                      end=datetime(2020, 3, 9), api_key=fuck)
# for var_key in env_vars.keys():
#     print(f'\nEnvVar_Key: {var_key}'
#           f'\n\tEnvVar_Val: {env_vars[var_key]}')
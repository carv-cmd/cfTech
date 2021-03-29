# AlphaVantage Connection

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())



class ConfigKey(object):
    def __init__(self):
        self.apikey = ""

    def __get__(self, instance, owner):
        return self.apikey

    def __set__(self, instance, value):
        self.apikey = os.getenv(f'{value}')

    def __str__(self):
        return f'API Key: {self.apikey}'


class ConfigInterval(object):
    def __init__(self):
        self.interval = "30min"

    def __get__(self, instance, owner):
        return self.interval

    def __set__(self, instance, value):
        self.interval = value

    def __str__(self):
        return f'Interval: {self.interval}'


class ConfigSetSize(object):
    def __init__(self):
        self.return_size = 'compact'

    def __get__(self, instance, owner):
        return self.return_size

    def __set__(self, instance, value):
        self.return_size = value

    def __str__(self):
        return f'Return Size: {self.return_size}'


class ConfigOutputFormat(object):
    def __init__(self):
        self.output_format = 'pandas'

    def __get__(self, instance, owner):
        return self.output_format

    def __set__(self, instance, value):
        self.output_format = value


class ConfigTicker(object):
    def __init__(self):
        self.ticker = "AAPL"

    def __get__(self, instance, owner):
        return self.ticker

    def __set__(self, instance, value):
        self.ticker = value

    def __str__(self):
        return f'Ticker: {self.ticker}'


def check_env_vars(self):
    """
    Having trouble accessing some stored environment variable? For example your API_key?
    Call this method to print all environment variables currently seen by the interpreter
    Easiest fix is to create a '.env' text file in project directory to store these key/pair values
    The 'dotenv' module loads the .env key/pair values as envVars into current working environment
    BE SURE to include '.env' in your '.gitignore' file or risk pushing your private key to a public repo
    Formatting of EnvVars: One liner w/ no whitespace from the margin:: KEY="<value>"
    API_KEY="6!9xj*457sfY62SD6f"
    """
    env_vars = os.environ
    for var_key in env_vars.keys():
        print(f'\nEnvVar_Key: {var_key}'
              f'\n\tEnvVar_Val: {env_vars[var_key]}')


class ConfigAll:
    key = ConfigKey()
    tick = ConfigTicker()
    interval = ConfigInterval()
    return_size = ConfigSetSize()
    formatting = ConfigOutputFormat()


class Configured(ConfigAll):
    condom = ConfigAll()

    def __init__(self):
        super().__init__()


def call_api():
    ready = Configured()
    ready.key = "ALPHAVANTAGE_API_KEY"


# class KeyConfig:
#     def __init__(self):
#         self.api_key = ""
#         self.symbol = "AAPL"
#         self.time_unit = "30min"
#         self.d_size = "compact"
#         self.forma = "pandas"
#
#     def get_api_key(self):
#         """ Returns current stored value for 'api_key' """
#         return self.api_key
#
#     def set_api_key(self, pick_api):
#         """ Pass .env variable with api key that you wish to connect to """
#         self.api_key = os.getenv(f'{pick_api}')
#
#     def hold_key(self, auto_api):
#         self.api_key = auto_api
#
#     def get_symbol(self):
#         """ Ticker symbol for stock """
#         return self.symbol
#
#     def get_unit(self):
#         """ Time Interval """
#         return self.time_unit
#
#     def get_size(self):
#         """ compact = last 100 data points """
#         return self.d_size
#
#     def get_forma(self):
#         """ Default data formatting is set to Pandas-DataFrame object """
#         return self.forma
#
#     def set_symbol(self, symbol):
#         """ Must be a valid ticker symbol listed on a known exchange """
#         self.symbol = symbol
#
#     def set_units(self, units):
#         """ Options: 1min - 5min - 15min - 30min - 60min """
#         self.time_unit = units
#
#     def set_size(self, size):
#         """ compact=last100pts ~ full=completeSet """
#         self.d_size = size
#
#     def set_forma(self, user_format):
#         """
#         Default value is pandas dataframe structures
#         Optional choice to set as a '.json' or '.csv' file
#         """
#         self.forma = user_format
#

#
#     def __str__(self):
#         return f'\nAPI KEY: {self.api_key}\n' \
#                f'\nTicker Symbol: {self.symbol}\n' \
#                f'\nInterval: {self.time_unit}\n' \
#                f'\nSet Size: {self.d_size}\n' \
#                f'\nOutput Format: {self.forma}' \
#                f'\nAPI KEY: {self.api_key}\n'

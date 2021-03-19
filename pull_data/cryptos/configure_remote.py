import os
from dotenv import load_dotenv, find_dotenv
from datetime import *
from alpha_vantage.cryptocurrencies import CryptoCurrencies
import pandas as pd
from pprint import pprint

load_dotenv(find_dotenv())


class SetInterval(object):
    """
    Use this class to initiate the 'Fetch' object time interval
    'start': historical point in time fetching back to, (start=)
    'end': date fetching up to. Default is now but can be set to any point in time
    """
    def __init__(self):

        self.start_day = date(2010, 1, 1)
        self.start_time = time(9, 0, 0)

        self.end_day = datetime.now().date()
        self.end_time = datetime.now().time()

    ##########################################
    ##########################################
    def get_start_day(self):
        """ Returns the current historical date fetching back to, where applicable """
        return self.start_day

    def get_start_time(self):
        """ Returns the current historical time on that date fetching back to """
        return self.start_time

    def get_end_day(self):
        """ Returns the current date fetching up to, where applicable """
        return self.end_day

    def get_end_time(self):
        """ Returns the current time on that date fetching up to """
        return self.end_time

    ##########################################
    ##########################################
    def set_start_day(self, s_year, s_month, s_day):
        """ Sets the interval starting day """
        self.start_day = date(s_year, s_month, s_day)

    def set_start_time(self, s_hour, s_min, s_sec):
        """ Sets the interval starting time. Default value is 9:00am when markets open. """
        self.start_time = time(s_hour, s_min, s_sec)

    def set_end_date(self, e_year, e_month, e_day):
        """ Set the interval end date. Default end datetime is time at program runtime """
        self.end_day = date(e_year, e_month, e_day)

    def set_end_time(self, s_hour, s_min, s_sec):
        """ Set the interval end time. Default end datetime is time at program runtime """
        self.end_time = time(s_hour, s_min, s_sec)

    ##########################################
    ##########################################
    def __str__(self):
        return f'\nInterval Start:\t{self.start_day.__str__()}\t{self.start_time.__str__()}\n' \
               f'\nInterval End:\t{self.end_day.__str__()}\t{self.end_time.__str__()}\n'


#########################################################################
#########################################################################
class Configs:
    def __init__(self):
        self.api_key = ""
        self.forma = 'pandas'

    ##########################################
    ##########################################
    def get_api_key(self):
        """ Returns current stored value for 'api_key' """
        return self.api_key

    def get_formatting(self):
        """ Default data formatting is set to Pandas-DataFrame object """
        return self.forma

    ##########################################
    ##########################################
    def set_api_key(self, pick_api):
        """ Pass api key .env variable that you wish to connect to """
        self.api_key = os.getenv(pick_api)

    def set_formatting(self, user_format):
        """ Default value is pandas dataframe structures """
        self.forma = user_format

    ##########################################
    ##########################################
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


#########################################################################
#########################################################################
class FetchData(Configs):
    def __init__(self):
        super().__init__()


#########################################################################
#########################################################################
class PushToDir:
    def __init__(self):
        self.reset = os.getcwd()
        self.dump_fin = os.getenv('TECH_DATA')[2:-1]
        self.dump_btc = os.getenv('BTC_DATA')[2:-1]
        self.export_data = pd.DataFrame()
        self.daters_name = "daters.csv"

    ##########################################
    ##########################################
    def get_export_data(self):
        return self.export_data

    def get_file_name(self):
        return self.daters_name

    def get_dump_fin(self):
        return self.dump_fin

    def get_dump_btc(self):
        return self.dump_btc

    def get_reset(self):
        return self.reset

    ##########################################
    ##########################################
    def set_export_data(self, daters):
        """ Call this method passing it the data object you wish to export """
        self.export_data = daters

    def set_file_name(self, file_name):
        self.daters_name = file_name

    def set_dump_fin(self, user_fin_dump):
        """ Best practice is creating an envVar which points to the folder you wish to store the data """
        self.dump_fin = user_fin_dump

    def set_dump_btc(self, user_btc_dump):
        """ Best practice is creating an envVar which points to the folder you wish to store the data """
        self.dump_btc = user_btc_dump

    ##########################################
    ##########################################
    def exporter(self):
        try:
            os.chdir(os.getenv("PUSH_DATA"))
            self.export_data.to_csv(self.get_file_name())
            os.chdir(self.get_reset())
        except FileNotFoundError or NotADirectoryError or ValueError:
            pass


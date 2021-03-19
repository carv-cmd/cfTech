import os
from dotenv import load_dotenv, find_dotenv
from datetime import *

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
        self.forma = "pandas"

    ##########################################
    ##########################################
    def get_api_key(self):
        """ Returns current stored value for 'api_key' """
        return self.api_key

    def get_forma(self):
        """ Default data formatting is set to Pandas-DataFrame object """
        return self.forma

    ##########################################
    ##########################################
    def set_api_key(self, pick_api):
        """ Pass api key .env variable that you wish to connect to """
        self.api_key = os.getenv(f'{pick_api}')

    # def set_forma(self, user_format):
    #     """ Default value is pandas dataframe structures """
    #     self.forma = user_format

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
class StepSize:
    def __init__(self):
        self.symbol = ""
        self.time_unit = ""
        self.df_size = ""

    def get_symbol(self):
        return self.symbol

    def get_unit(self):
        return self.time_unit

    def get_size(self):
        return self.df_size

    ##########################################
    ##########################################
    def set_symbol(self, symbol):
        self.symbol = symbol

    def set_units(self, units):
        self.time_unit = units

    def set_size(self, size):
        self.df_size = size

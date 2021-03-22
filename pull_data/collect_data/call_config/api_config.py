import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class APIConfig:
    def __init__(self):
        self.api_key = ""

    def get_api_key(self):
        """ Returns current stored value for 'api_key' """
        return self.api_key

    def set_api_key(self, pick_api):
        """ Pass .env variable with api key that you wish to connect to """
        self.api_key = os.getenv(f'{pick_api}')

    def hold_key(self, auto_api):
        self.api_key = auto_api

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

    def __str__(self):
        return f'\nAPI KEY: {self.api_key}\n'

import os
import random
import string
from dotenv import load_dotenv, find_dotenv


def gen_password(length=16):
    """
    Use to generate randomized passwords for API credentials
    DO NOT SAVE PASSWORDS ARBITRARILY IN PROJECT
    Instead create a .env file and include the file extension in your .gitignore file
    :param: len(password), default = 16
    :return: randomized password
    """
    chars = string.ascii_letters + string.digits + '!@#$%&*'
    random.seed = (os.urandom(1024))

    return ''.join(random.choice(chars) for i in range(length))


def check_env():
    """
    Prints all available environment variables
    Env Var 'key' and its 'value'
    """
    load_dotenv(find_dotenv())
    env_vars = os.environ

    for var_key in env_vars.keys():
        print(f'\nEnvVar_Key: {var_key}'
              f'\n\tEnvVar_Val: {env_vars[var_key]}')
    return


if __name__ == "__main__":
    # print('\nChecking Current Environment Variables!\n')
    # check_env()
    print(f'Username={gen_password(10)}')
    print(f'Password={gen_password(24)}')

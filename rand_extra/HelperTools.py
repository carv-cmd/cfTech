import os
import random
import string
from collections import defaultdict


def quick_pins(pin_len: int):
    """ Quick and dirty pin numbers. Not secure! """
    nums = string.digits
    random.seed(os.urandom(1024))
    return ''.join(random.choice(nums) for quick_pin in range(pin_len))


def gen_credentials(name_len: int, pass_len: int):
    """
    Quick and dirty credentials.
    If security is essential, this is not ideal.
    :param: name_len: Length of Username, [default=16]
    :param: pass_len: Length of Password, [default=24]
    :return: dict object with Username and Password key/pair values
    """

    chars = string.ascii_letters + string.digits

    random.seed = (os.urandom(1024))
    username = ''.join(random.choice(chars) for user_name in range(name_len))

    random.seed = (os.urandom(1024))
    password = ''.join(random.choice(chars + '!@#$%&*') for pass_word in range(pass_len))

    return {"Username": username, "Password": password}


def check_env(printer=False, key=""):
    """
    Verify 'dotenv' functionality. Import and run in script w/ dotenv import
    Add [ TEST_KEY="E8gHLu6LjTDega" ] to the .env file created and then test function calls below.
        Empty function call returns complete environment variable dictionary.
        print_it is True & key is None: Print environment variable dictionary to console.
        print_it & key both not None: Print key/value pair if key exists and return value.
        if key is True and not print_it: return value if key exists.
    """
    print('\nChecking Current Environment Variables!\n')
    env_vars = os.environ
    if key:
        try:
            val = env_vars[key]
            return val
        except KeyError:
            print(f'\n>> enVar[{key}] does not exist')
    elif printer:
        for key in env_vars.keys():
            print(f'\nEnvVar:\n\t[ Key: {key} ]\n\t[ Val: {env_vars[key]} ]')
    else:
        return env_vars


if __name__ == "__main__":
    # for xyz in range(100):
    #    print([quick_pins(6) for i in range(12)])
    # print(gen_credentials(name_len=16, pass_len=12))

    # GENERATE PSEUDO-RANDOM CREDENTIALS
    # print(f'\nGenerating Credentials!\n'
    #       f'\nNew Credentials: {gen_credentials(12, 16)}\n')
    
    # PASS ENVIRONMENT VARIABLE KEY TO CHECK IF IT EXISTS, AND RETURN THE VALUE
    # _query = 'TEST_KEY'
    # testkey = check_env(key=_query)
    # print(f'EnVar[{_query}]="{testkey}')
    
    # PRINT ALL ENVIRONMENT VARIABLES
    check_env(printer=True)
    
    # GET ENVIRONMENT VARIABLES DICTIONARY
    # checked = check_env()
    # print(f'EnvVars Dict:\n{checked}')

else:
    pass

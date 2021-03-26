import os
import random
import string


def gen_password(name_len=16, pass_len=24):
    """
    Use to generate randomized user name and passwords for API credentials
    DO NOT SAVE THESE VALUES ARBITRARILY WITHIN THE PROJECT. See 'check_env()' docstring for details
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


def check_env(key='', print_it=''):
    """
    Create a '.env' file in the project and add that extension .gitignore file
    Safer and easier way to manage API keys locally w/o risking a push to public repo
    Use these variables as a way to store commonly accessed directories as well
    This function verifies they're seen by the interpreter

    Dependencies for '.env' usage:
        * from dotenv import load_dotenv, find_dotenv
        * load_dotenv(find_dotenv())

    Add this to .env then pass key to func for testing, works with any envVar
        * TEST_KEY="E8gHLu6LjTDega"

    Prints a single key pair value, and returns just the key
    Prints all environment key/pair values
    :returns: dict w/ env key/pairs as the dict key/pairs
    """
    print('\nChecking Current Environment Variables!\n')

    env_vars = os.environ
    if key is not '':
        print(f'{key}="{env_vars[key]}"')
        return env_vars[key]

    elif print_it is not 'yes':
        return env_vars

    else:
        for var_key in env_vars.keys():
            print(f'\nEnvVar_Key: {var_key}'
                  f'\n\tEnvVar_Val: {env_vars[var_key]}')
    return


if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())

    check_env(key='TEST_KEY')
    print(f'\nGenerating Credentials!\n'
          f'\nNew Credentials: {gen_password(12, 16)}\n')

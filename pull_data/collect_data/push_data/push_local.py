# Turns Pandas.DataFrames into JSON objects
# Returns object or creates a json file in working directory
import pandas as pd
from pprint import pprint


class ExpoConfigs:
    """
    Descriptor class to set the to_json properties
    Defaults: oriented="index", date_form="iso", filename="testName"
    Oriented: [‘split’, ‘records’, ‘index’, ‘columns’, ‘values’, ‘table’]
    DateFormat: [’ISO8601 (iso)’, ’epoch’, ’None’]
    FileName: ONLY pass the desired file name; .JSON file ext automatically added
    """
    def __init__(self, filename='fuck', oriented='index', date_form='iso'):
        self.filename = filename
        self.oriented = oriented
        self.date_form = date_form

    def __set__(self, instance, **kwargs):
        self.oriented = kwargs['oriented']
        self.date_form = kwargs['date_form']
        self.filename = "{}.JSON".format(kwargs['filename'])

    def make_json(self, data):
        return data.to_json(orient=self.oriented, date_format=self.date_form)

    def local_dir(self, data):
        try:
            data.to_json(self.filename, orient=self.oriented, date_format=self.date_form)

        except FileNotFoundError or NotADirectoryError or ValueError:
            print('Transaction FAILED!')

    def __str__(self):
        return f"\n'FileName': {self.filename}\n" \
               f"\n'Orientation': {self.oriented},\n" \
               f"\n'DateFormatting': {self.date_form},\n"


class MakeJSON(ExpoConfigs):
    """ Pass the desired JSON attributes to a .create() instance """
    create = ExpoConfigs


def push_local(data, **kwargs):
    try:
        go_local = MakeJSON()
        go_local.create(filename=kwargs['filename'], oriented=kwargs['oriented'], date_form=kwargs['date_form'])
        go_local.local_dir(data)

    except AttributeError or ValueError:
        print('Push Operation FAILED!!!')


def json_object(data, **kwargs):
    """ Pass the DataFrame object """
    try:
        json_obj = MakeJSON()
        json_obj.create(oriented=kwargs['oriented'], date_form=kwargs['date_form'])
        return json_obj.make_json(data)

    except AttributeError or ValueError:
        print('Push Operation FAILED!!!')


if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())

    dati = pd.DataFrame([['a', 'b'], ['c', 'd']],
                        index=['row 1', 'row 2'],
                        columns=['col 1', 'col 2'])

    print(f'\nStarting Test Push...')
    boop = json_object(dati)
    print('\nBoop Instance:\n')
    pprint(boop)
    print(f'\nFinished Test Push...')

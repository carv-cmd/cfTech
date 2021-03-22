import os
from api_config import *
# import pandas as pd


#########################################################################
#########################################################################
class SetDirectory:
    def __init__(self):
        self.reset = os.getcwd()
        self.dump_dir = ""

    def target_dir(self):
        os.chdir(os.getenv(self.dump_dir)[2:-1])

    def switch_back(self):
        os.chdir(self.reset)

    def get_dir(self):
        return self.dump_dir

    def set_dir(self, dump):
        self.dump_dir = dump

    def __str__(self):
        return f'Dump Directory: {self.dump_dir}'


#########################################################################
#########################################################################
class PushToDir(SetDirectory):
    def __init__(self):
        super().__init__()
        self.daters_name = "daters.csv"

    ##########################################
    ##########################################
    def get_export_structure(self):
        return self.export_data

    def get_file_name(self):
        return self.daters_name

    ##########################################
    ##########################################
    def set_export_data(self, daters):
        """ Call this method passing it the data object you wish to export """
        self.export_data = daters

    def set_file_name(self, file_name):
        self.daters_name = file_name

    ##########################################
    ##########################################
    def export_json(self):
        try:
            pass
        except FileNotFoundError or NotADirectoryError or ValueError:
            pass

    def export_csv(self):
        try:
            os.chdir(os.getenv(self.get_dir()))
            self.export_data.to_csv(self.get_file_name())
        except FileNotFoundError or NotADirectoryError or ValueError:
            print('dumb fuck head')
            pass


#########################################################################
#########################################################################
def test_func(dir):
    test = SetDirectory()
    test.set_dir(dir)
    test.target_dir()
    print(f'\nDirectory after target call: {os.getcwd()}')
    info = input('Look correct??? ')
    test.switch_back()
    print(f'Directory after switch call: {os.getcwd()}')


#########################################################################
#########################################################################
if __name__ == "__main__":
    print()
    # test_func('PUSH_DATA')

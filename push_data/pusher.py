import os
import pandas as pd


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
            print('dumb fuck head')
            pass
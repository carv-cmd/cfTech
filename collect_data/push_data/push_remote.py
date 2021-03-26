import os


class SetDir:
    """
    Descriptor class for SetupJSON:
    Sets Directory in 'Pandas->JSON' conversion task
    """

    reset = os.getcwd()

    def __init__(self, dump_to="PUSH_DATA"):
        """ Pass the .env variable where your dump directory is stored """
        self.dump_to = os.getenv(dump_to)[2:-1]

    def __get__(self, instance, owner):
        """ Returns the current data dump directory """
        return self.dump_to

    def __set__(self, instance, value):
        """ Set the data dump directory, ideal to use path variables """
        self.dump_to = value

    def change_dir(self):
        """
        Stored directory in .env file as r-string, hence the slicing
        Create pseudo path variables in .env file to load in workspace as env variables
        """
        try:
            os.chdir(self.dump_to)
            print(f'\nTaking a dump in: {os.getcwd()}')

        except TypeError:
            print('chdir task FAILED...')
            raise

    def reset_dir(self):
        """
        Call 'reset_dir' method after executing operations following 'change_dir' method call
        Resets to the initial CWD program started in
        """
        os.chdir(self.reset)
        print(f'Returned to: {self.reset}')

    def __str__(self):
        return f'\nDump Directory: {self.dump_to}'

# class ChangeDir(SetDir):
#     """
#     Set the target directory bu passing the .env variable to .set_target method
#     Call 'change_dir' and 'reset_dir' methods ChangeDir inst to quickly access dumps in memory
#     A generalized way of accessing .env variables w/ goal of being more machine agnostic
#     Example:
#                 switcher = ChangeDir().set_target(dump_to="BTC_DATA")
#                 switcher.change_dir()
#                 <take_a_dump_now>
#                 switcher.reset_dir()
#     """
#
#     set_target = SetDir
#
#     def __str__(self):
#         return f'Target Directory: {self.dump_to}'

class Exporter(ExpoConfigs):

    def __init__(self):
        super().__init__()

    def local_dir(self, data):
        try:
            data.to_json(self.filename, orient=self.oriented, date_format=self.date_form)

        except FileNotFoundError or NotADirectoryError or ValueError:
            print('Transaction FAILED!')

    def remote_dir(self, data, target):
        try:
            target.change_dir()
            data.to_json(self.filename, orient=self.oriented, date_format=self.date_form)
            target.reset_dir()

        except FileNotFoundError or NotADirectoryError or ValueError:
            print('Transaction FAILED!')
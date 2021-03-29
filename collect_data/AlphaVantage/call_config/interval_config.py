from datetime import *
from api_config import *


class SetInterval:
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

    def __str__(self):
        return f'\nInterval Start:\t{self.start_day.__str__()}\t{self.start_time.__str__()}\n' \
               f'\nInterval End:\t{self.end_day.__str__()}\t{self.end_time.__str__()}\n'


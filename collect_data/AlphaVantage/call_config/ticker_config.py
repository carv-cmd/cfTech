class TickConfig:
    def __init__(self):
        self.symbol = "AAPL"
        self.time_unit = "30min"
        self.d_size = "compact"
        self.forma = "pandas"

    def get_symbol(self):
        """ Ticker symbol for stock """
        return self.symbol

    def get_unit(self):
        """ Time Interval """
        return self.time_unit

    def get_size(self):
        """ compact = last 100 data points """
        return self.d_size

    def get_forma(self):
        """ Default data formatting is set to Pandas-DataFrame object """
        return self.forma

    def set_symbol(self, symbol):
        """ Must be a valid ticker symbol listed on a known exchange """
        self.symbol = symbol

    def set_units(self, units):
        """ Options: 1min - 5min - 15min - 30min - 60min """
        self.time_unit = units

    def set_size(self, size):
        """ compact=last100pts ~ full=completeSet """
        self.d_size = size

    def set_forma(self, user_format='pandas'):
        """
        Default value is pandas dataframe structures
        Optional choice to set as a '.json' or '.csv' file
        """
        self.forma = user_format

    def __str__(self):
        return f'\nTicker Symbol: {self.symbol}\n' \
               f'\nInterval: {self.time_unit}\n' \
               f'\nSet Size: {self.d_size}\n' \
               f'\nOutput Format: {self.forma}'

# ** Identify reserve/hidden orders within L2 quotes
# ** Shadow trade these positions as they will provide market support and resistance
import re
from tkinter import *
from tkinter import ttk
from typing import Any

import logging
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s')
# _COL, _ROW, _CSPAN, _RSPAN = (PARM['COL'], PARM['ROW'], PARM['CSPAN'], PARM['RSPAN'])
# _LEFT, _RIGHT, _VERT, _HORZ = (PARM['LEFT'], PARM['RIGHT'], PARM['VERT'], PARM['HORZ'])
# _HI, _WIDE, _WEIGHT = (PARM['HEIGHT'], PARM['WIDTH'], PARM['WEIGHT'])
# _PADX, _PADY = PARM['PADX'], PARM['PADY']
# _MARKETS = PARM['MARKETS']
# (_COL, _CSPAN, _PADX, _ROW, _RSPAN, _PADY, _LEFT,
#  _RIGHT, _VERT, _HORZ,_HI, _WIDE, _WEIGHT, _MARKETS)
# _MKTS = ('BTC/USD', 'BTC/USDT', 'BTC-PERP', 'BTC/TRYB',
#          'ETH/BTC', 'ETH/USD', 'ETH/USDT', 'ETH-PERP')


def quick_config(grid=False, stix=False, others=False):
    param = {
        'COL': 0, 'CSPAN': 2, 'PADX': 4,
        'ROW': 0, 'RSPAN': 9, 'PADY': 1,
        'HEIGHT': 8, 'WIDTH': 12, 'WEIGHT': 1,
        'LEFT': W, 'RIGHT': E, 'VERT': (N, S), 'HORZ': (W, E),
        'MARKETS': (
            'BTC/USD', 'BTC/USDT', 'BTC-PERP', 'BTC/TRYB',
            'ETH/BTC', 'ETH/USD', 'ETH/USDT', 'ETH-PERP')
    }
    if grid:
        return param['COL'], param['CSPAN'], param['PADX'], param['ROW'], param['RSPAN'], param['PADY']
    elif stix:
        return param['LEFT'], param['RIGHT'], param['VERT'], param['HORZ']
    elif others:
        return param['HEIGHT'], param['WIDTH'], param['WEIGHT']
    else:
        return param['MARKETS']


class RootsMain(Tk):
    """ TODO: Exception raised by most tk errors is tk.TclError """
    _TITLE = 'Medium Rare Hot Dog'
    _LfConfig = {'sock': 'WebSocket-API', 'rest': 'REST-API', 'data': 'DataFrame'}
    _PADS = '3 3 12 12'
    _MMM = quick_config()

    def __init__(self):
        super().__init__()
        self._valid = None
        self._mains = ttk.Frame(self.winfo_toplevel(), padding=self._PADS)
        self._sockframe = ttk.Labelframe(self._mains, padding=self._PADS)
        self._restframe = ttk.LabelFrame(self._mains, padding=self._PADS)
        self._dataframe = ttk.LabelFrame(self._mains, padding=self._PADS)
        self._ui_frames()

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def _ui_frames(self, pax=2, pay=2, stix=(N, S, W, E)):
        assert self._mains is not None, 'need a _mains to launch silly'
        self.title(self._TITLE)
        self.winfo_toplevel().columnconfigure(0, minsize=400, weight=1)
        self.winfo_toplevel().rowconfigure(0, minsize=250, weight=1)
        self._frame_config(
            self._mains, col=0, padx=pax, row=0, pady=pay, stix=stix,
            row_col=[(1, 1), (1, 1)], mins=200)
        self._frame_config(
            self._sockframe, col=0, padx=pax, row=0, pady=pay, stix=NW,
            row_col=[(1, 1), (1, 1)], mins=100, text=self._LfConfig['sock'])
        self._frame_config(
            self._restframe, col=1, padx=pax, row=0, pady=pay, stix=NE,
            row_col=[(1, 1)], mins=100, text=self._LfConfig['rest'])
        self._frame_config(
            self._dataframe, col=0, padx=pax, row=1, pady=pay, stix=SW,
            row_col=[(1, 1)], mins=100, text=self._LfConfig['data'])

    @staticmethod
    def _get_tk_vars(variable, **kwargs):
        pass

    @staticmethod
    def _frame_config(frame, col: int, padx: int, row: int, pady: int, stix: tuple,
                      row_col: list, mins: int = 300, cspan=1, rspan=1, text: str = None):
        frame.grid(
            column=col, columnspan=cspan, padx=padx, row=row, rowspan=rspan, pady=pady, sticky=stix)
        for index in range(len(row_col)):
            frame.columnconfigure(index, minsize=mins, weight=row_col[index][0])
            frame.rowconfigure(index, weight=row_col[index][1])
        if type(frame) is ttk.LabelFrame:
            frame.configure(text=text)

    @staticmethod
    def _get_separator(frame, orient: Any, column: int, cspan: int, padx: int,
                       row: int, rspan: int, pady: int, stix: Any):
        _mkt_separator = ttk.Separator(frame, orient=orient).grid(
            column=column, columnspan=cspan, padx=padx,
            row=row, pady=pady, rowspan=rspan, sticky=stix)

    @staticmethod
    def _get_label(frame, text: str, column: int, padx: int,
                   row: int, pady: int, stix: Any):
        _label = ttk.Label(frame, text=text).grid(
            column=column, padx=padx, row=row, pady=pady, sticky=stix)

    @staticmethod
    def _get_spinbox(frame, width: int, txtvar: StringVar, low: float, high: float,
                     column: int, padx: int, row: int, pady: int, stix: Any):
        _spins = ttk.Spinbox(frame, from_=low, to=high, width=width, textvariable=txtvar)
        _spins.grid(column=column, padx=padx, row=row, pady=pady, sticky=stix)

    @staticmethod
    def _get_radiobutton(frame, text: str, variable: StringVar, value: Any,
                         column: int, padx: int, row: int, pady: int, stix: Any):
        _radio = ttk.Radiobutton(frame, text=text, variable=variable, value=value.lower())
        _radio.grid(column=column, padx=padx, row=row, pady=pady, sticky=stix)
        _radio.bind('<Activate>', _radio.state(['!disabled', 'selected']))
        _radio.bind('<ButtonPress-1> <Deactivate>', _radio.state(['!selected']))

    @staticmethod
    def _get_button(frame, text: str, cmd: Any, width: int,
                    column: int, padx: int, row: int, pady: int, stix: Any):
        _insert = ttk.Button(frame, text=text, width=width, command=cmd).grid(
            column=column, padx=padx, row=row, pady=pady, sticky=stix)

    @staticmethod
    def inspect_widget(_widget_obj, slave=False, size=False):
        if slave:
            logging.debug(f'>>> newFrame.grid_slaves = {_widget_obj.grid_slaves()}')
        if size:
            logging.debug(f'>>> newFrame.grid_size = {_widget_obj.grid_size()}')

    def _get_combo(self, frame, listed: tuple, strvar: StringVar, width: int, height: int,
                   column: int, padx: int, row: int, pady: int, stix: Any):
        _combo = ttk.Combobox(
            frame, height=height, width=width,
            textvariable=strvar, validate='key',
            validatecommand=(self.register(self._checks), '%P'))
        _combo.grid(column=column, padx=padx, row=row, pady=pady, sticky=stix)
        _combo["values"] = listed
        self._valid = _combo.register(self._checks)

    @staticmethod
    def _checks(func, update):
        def check_wrap(update):
            logging.debug(f'>>> THE FUCK IS THIS:')
            return re.match("([A-Z\d])[-/]?", update) is not None and len(update) < 18
        return check_wrap(update)


class FtxSOCK(RootsMain):
    _COL, _CSPAN, _PADX, _ROW, _RSPAN, _PADY = quick_config(grid=True)
    _LEFT, _RIGHT, _VERT, _HORZ = quick_config(stix=True)
    _HI, _WIDE, _WEIGHT = quick_config(others=True)
    _MARKETS = quick_config()
    _SPIN_RADIO = ['--Select Channels --', '- Polling Interval -']

    def __init__(self):
        super().__init__()
        assert self._mains is not None, 'need a _mains to launch silly'
        self._sock_vars()
        self._sock_market()
        self._sock_channel()
        self._sock_buttons()

    def _sock_vars(self):
        self._market_str = StringVar(self._mains)
        self._spin_ordbk_dub = DoubleVar(self._mains)
        self._spin_trades_dub = DoubleVar(self._mains)
        self._spin_tickers = DoubleVar(self._mains)
        self._radio_ordbk = StringVar(self._mains, value='orderbook', name='Orderbook')
        self._radio_trades = StringVar(self._mains, value='trades', name='Trades')
        self._radio_tickers = StringVar(self._mains, value='tickers', name='Tickers')

    def _sock_market(self, col=_COL, cspan=_CSPAN, rspan=_RSPAN, pax=_PADX, row=_ROW, pay=_PADY,
                     hi=_HI, width=_WIDE, left=_LEFT, vert=_VERT, horz=_HORZ, markets=_MARKETS):
        _separators = [
            (VERTICAL,    2,   0,   1,        rspan,    vert),
            (VERTICAL,    4,   0,   1,        rspan,    vert),
            (HORIZONTAL,  0,   1,   cspan,    1,        horz),
            (HORIZONTAL,  3,   1,   1,        1,        horz)
        ]
        for orientation, cols, ros, col_span, row_span, stik in _separators:
            self._get_separator(
                frame=self._sockframe, orient=orientation, column=cols, cspan=col_span, padx=pax,
                row=ros, rspan=row_span, pady=pay, stix=stik)
        self._get_label(
            frame=self._sockframe, text='Enter/Select Market:',
            column=col, padx=pax, row=row, pady=pay, stix=left)
        self._get_combo(frame=self._sockframe, listed=markets, strvar=self._market_str, width=width,
                        height=hi, column=col + 1, padx=pax, row=row, pady=pay, stix=left)
        self._get_button(
            frame=self._sockframe, text='Insert', width=width, cmd=self._inserts,
            column=col+3, padx=pax, row=row, pady=pay, stix=horz)

    def _sock_channel(self, col=_COL, pax=_PADX, row=_ROW+2, cspan=_CSPAN, pay=_PADY+2,
                      width=_WIDE, stix=_LEFT, horz=_HORZ, iters=1):
        self._get_separator(
            frame=self._sockframe, orient=HORIZONTAL, column=col, cspan=cspan, padx=pax,
            row=row+7, rspan=1, pady=pay, stix=horz)
        for index in range(len(self._SPIN_RADIO)):
            self._get_label(
                frame=self._sockframe, text=self._SPIN_RADIO[index],
                column=col+index, padx=pax, row=row, pady=pay, stix=stix)
        for spins, radios in ([self._spin_ordbk_dub, self._radio_ordbk],
                              [self._spin_trades_dub, self._radio_trades],
                              [self._spin_tickers, self._radio_tickers]):
            self._get_spinbox(
                frame=self._sockframe, width=width, txtvar=spins, low=0.0, high=300.0,
                column=col, padx=pax, row=row+iters, pady=pay, stix=stix)
            self._get_radiobutton(
                frame=self._sockframe, text=radios, variable=radios, value=radios.get(),
                column=col+1, padx=pax, row=row+iters, pady=pay, stix=stix)
            iters += 1

    def _sock_buttons(self, width=_WIDE, pax=_PADX, pay=_PADY, stix=W):
        _row_config, irs = [10, 10], [0, 0]
        _button_helper = [('Unsubscribe', self._unsub), ('Subscribe', self._subs)]
        for butt in range(len(_button_helper)):
            btn, act = _button_helper[butt][0], _button_helper[butt][1]
            self._get_button(
                frame=self._sockframe, text=_button_helper[butt][0], width=width, cmd=act,
                column=butt+irs[butt], padx=pax, row=_row_config[butt], pady=pay, stix=stix)

    def _inserts(self):
        try:
            print(f'\n>>> _INSERTS(the naked man fears no pickpocket)')
            self.inserts()
        except AttributeError as e:
            logging.debug(f'>>> Exception in _inserts: {e}')

    def _subs(self):
        try:
            print(f'\n>>> _SUBS._EVENT_HANDLER. . .')
            self.inserts()
        except Exception as e:
            logging.debug(f'>>> Exception in _subs: {e}')

    def _unsub(self):
        try:
            print(f'\n>>> _UNSUB._EVENT_HANDLER')
            self.inserts()
        except Exception as e:
            logging.debug(f'>>> Exception in _unsub: {e}')

    def inserts(self):
        print(f'\n>>> {self._market_str.get()}'
              f'\n>>> {self._spin_ordbk_dub.get()}, {self._radio_ordbk.get()}'
              f'\n>>> {self._spin_trades_dub.get()}, {self._radio_trades.get()}'
              f'\n>>> {self._spin_tickers.get()}, {self._radio_tickers.get()}')

    def launch_mainloop(self):
        assert self._mains is not None, 'need a _mains to launch silly'
        self.mainloop()


class FtxREST(RootsMain):
    _COL, _CSPAN, _PADX, _ROW, _RSPAN, _PADY = quick_config(grid=True)
    _LEFT, _RIGHT, _VERT, _HORZ = quick_config(stix=True)
    _HI, _WIDE, _WEIGHT = quick_config(others=True)
    _MARKETS = quick_config()
    _REST_LABELS = ['Endpoint:', 'Market:', 'Resolution:', 'Limit:', 'Start:', 'End:']
    _REST_EP = ("list_markets", "get_single_market", "get_orderbook", "get_trades", "get_historical",
                "get_options_vol_24hr", "get_options_vol_hist_btc", "get_options_open_interest",
                "get_options_hist_open_interest", "get_pub_options_trades", "get_options_fills",
                "list_futures", "get_future", "get_future_stats", "get_funding_rates", "get_hist_index",
                "spot_margin_mkt_info", "get_account_info", "get_positions", "get_open_orders",
                "get_open_triggers", "get_trigger_history", "get_trigger_triggers")

    def __init__(self):
        super().__init__()
        assert self._mains is not None, 'need a _mains to launch silly'
        self._set_rest_vars()
        self._set_rest_labels()
        self._set_rest_entries()

    def _set_rest_vars(self):
        self._rest_endpoint = StringVar(self._mains)    # _from_ComboBox -> EVENT-DRIVER
        self._rest_market = StringVar(self._mains)      # _from_ComboBox -> EventDriven
        self._rest_resolution = StringVar(self._mains)  # _from_SpinBox  -> EventDriven
        self._rest_limit = StringVar(self._mains)       # _from_SpinBox  -> EventDriven
        self._rest_start = IntVar(self._mains)          # _from_SpinBox  -> EventDriven
        self._rest_end = IntVar(self._mains)            # _from_SpinBox  -> EventDriven
        self._rest_endpoint.trace_add('write', self._checks)
        self._rest_market.trace_add('write', self._checks)

    def _set_rest_labels(self, col=_COL, pax=_PADX, row=_ROW, pay=_PADY, left=_LEFT):
        for lab in range(len(self._REST_LABELS)):
            self._get_label(
                self._restframe, text=self._REST_LABELS[lab],
                column=col, padx=pax, row=row+lab, pady=pay, stix=W)

    def _set_rest_entries(self, markets=_MARKETS, width=_WIDE, hi=_HI,
                          col=_COL+1, pax=_PADX, row=_ROW, pay=_PADY+2, stix=_RIGHT,
                          ending=_REST_EP):
        """
        TODO alwaysEnabled:method
            -> (rest_method: str = None)
        TODO defaultDisabled:params
            -> (market: str, ?resolution?: int, ?limit?: int, ?start?: int, ?end?: int)
        """
        self._get_combo(
            self._restframe, listed=ending, strvar=self._rest_endpoint, width=width + 18,
            height=hi, column=col, padx=pax, row=row, pady=pay, stix=stix)
        self._get_combo(
            self._restframe, listed=markets, strvar=self._rest_market, width=width,
            height=hi, column=col, padx=pax, row=row + 1, pady=pay, stix=stix)
        self._get_spinbox(  # resolution entry
            self._restframe, width=width, txtvar=self._rest_resolution,
            low=0, high=100, column=col, padx=pax, row=row+2, pady=pay, stix=stix)
        self._get_spinbox(  # limit entry
            self._restframe, width=width, txtvar=self._rest_limit,
            low=0, high=100, column=col, padx=pax, row=row+3, pady=pay, stix=stix)
        # TODO set iso date formatting for start and end, I think..
        # start entry
        # end entry


class FtxApp(FtxSOCK, FtxREST):
    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    ftx_Tk = FtxApp()
    # print(f'\n>>> dir(ftx_Tk):\n{dir(ftx_Tk)}')
    ftx_Tk.mainloop()


# for sep in range(2, 6, 2):
#     _content_separators = ttk.Separator(self._sockframe, orient=VERTICAL).grid(
#         column=col+sep, padx=pax, row=row, rowspan=rspan, sticky=vert)
# _mkt_separator = ttk.Separator(self._sockframe, orient=HORIZONTAL).grid(
#     column=col, columnspan=cspan, padx=pax, row=1, pady=pay+3, sticky=horz)
# _combo = ttk.Combobox(self._sockframe, height=hi, width=wid, textvariable=self._market_str)
# _combo.grid(column=col, padx=pax, row=row, pady=pay, sticky=right)
# _combo["values"] = markets
# _butt_separator = ttk.Separator(
#     self._sockframe, orient=VERTICAL).grid(
#     column=col+2, padx=pax, row=row, rowspan=rspan, sticky=vert)
# _data_separator = ttk.Separator(
#     self._sockframe, orient=VERTICAL).grid(
#     column=col+4, padx=pax, row=row, rowspan=rspan, sticky=vert)
# _mkt_label = ttk.Label(
#     self._sockframe, text='Enter/Select Market --').grid(
#     column=col, padx=pax, row=row, pady=pay, sticky=stix)
# _combo = ttk.Combobox(
#     self._sockframe, height=height, width=width, textvariable=self._market_str)
# _combo.grid(column=col+1, padx=pax, row=row, pady=pay, sticky=stix)
# _combo["values"] = markets
#
# _mkt_separator = ttk.Separator(self._sockframe, orient=HORIZONTAL).grid(
#     column=0, columnspan=cspan, padx=pax, row=2, pady=pay+3, sticky=(W, E))
# _insert_separator = ttk.Separator(self._sockframe, orient=HORIZONTAL).grid(
#     column=3, columnspan=1, padx=pax, row=2, pady=pay+3, sticky=(W, E))
# from tkinter import *
# from tkinter import ttk
#
# from pprint import pprint
# import logging
# logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s')
#
#
# class RootsMain(Tk):
#     # _ROOTS = Tk()
#
#     def __init__(self,
#                  userframe: Frame = None,
#                  streamframe: Frame = None,
#                  market_str: StringVar = None,
#                  spin_ordbk_dub: DoubleVar = None,
#                  spin_trades_dub: DoubleVar = None,
#                  spin_tickers_dub: DoubleVar = None,
#                  radio_ordbk_bool: BooleanVar = None,
#                  radio_trades_bool: BooleanVar = None,
#                  radio_tickers_bool: BooleanVar = None,
#     ):
#         super().__init__()
#         self._mains = ttk.Frame(self, padding='3 3 12 12')
#         self._sockframe = userframe
#         self._streamframe = streamframe
#         self._market_str = market_str
#         self._spin_ordbk_dub = spin_ordbk_dub
#         self._spin_trades_dub = spin_trades_dub
#         self._spin_tickers = spin_tickers_dub
#         self._radio_ordbk = radio_ordbk_bool
#         self._radio_trades = radio_trades_bool
#         self._radio_tickers = radio_tickers_bool
#
#     def __setattr__(self, key, value):
#         logging.debug(f'>>> __setattr__[key={key}, value={value}]')
#         self.__dict__[key] = value
#
#     def _configure_mainframe(self, border_width: int = 5, stix: tuple = (N, W, E, S)):
#         self.title('COCKFUCKER')
#         self._mains.grid(column=0, row=0, sticky=stix)
#         self._mains['borderwidth'] = border_width
#         self.columnconfigure(0, weight=1)
#         self.rowconfigure(0, weight=1)
#
#
# class UserFrame(RootsMain):
#     _STIX = NW
#     (_HI, _WIDE, _WEIGHT) = (8, 12, 1)
#     (_COL, _ROW, _CSPAN, _RSPAN, _PADX, _PADY) = (0, 1, 2, 1, 4, 2)
#     _MKTS = ('BTC/USD', 'BTC/USDT', 'BTC-PERP', 'BTC/TRYB',
#                 'ETH/BTC', 'ETH/USD', 'ETH/USDT', 'ETH-PERP')
#
#     def __init__(self):
#         super().__init__()
#         self._sockframe = ttk.Frame(getattr(self, '_mains'), padding='3 3 12 12')
#         self._market_str = StringVar(self._mains)
#         self._spin_ordbk_dub = DoubleVar(self._mains)
#         self._spin_trades_dub = DoubleVar(self._mains)
#         self._spin_tickers = DoubleVar(self._mains)
#         self._radio_ordbk = BooleanVar(self._mains)
#         self._radio_trades = BooleanVar(self._mains)
#         self._radio_tickers = BooleanVar(self._mains)
#
#     def _configure_userframe(self, border=5, stix=(N, W, E, S)):
#         self._sockframe.grid(column=0, row=0, sticky=stix)
#         self._sockframe.columnconfigure(0, weight=1)
#         self._sockframe.rowconfigure(0, weight=1)
#         self._sockframe['borderwidth'] = border
#
#     def _set_market(self, height=_HI, width=_WIDE, col=_COL, pax=_PADX,
#                     row=_ROW, pay=_PADY, stix=_STIX, markets=_MKTS):
#         _mkt_label = ttk.Label(
#             self._sockframe, text='-- Market Name --').grid(
#             column=col, padx=pax, row=row, pady=pay, sticky=stix)
#         _combo = ttk.Combobox(
#             self._sockframe, height=height, width=width, textvariable=self._market_str)
#         _combo.grid(column=col+2, padx=pax, row=row, pady=pay, sticky=stix)
#         _combo["values"] = markets
#         _queued = ttk.Button(
#             self._sockframe, text='Insert', width=width, command=print('foo')).grid(
#             column=col+4, padx=pax, row=row, pady=pay, sticky=(N, E))
#
#   def _set_channel(self, col=_COL, pax=_PADX, row=_ROW+1, pay=_PADY, width=_WIDE, stix=_STIX, iters=2):
#         _channel_options = ['-- Select Channels --', 'Set Delay', 'Poll(y/n)']
#         _channels = {'Orderbook': [self._spin_ordbk_dub, self._radio_ordbk],
#                      'Trades': [self._spin_trades_dub, self._radio_trades],
#                      'Tickers': [self._spin_tickers, self._radio_tickers]}
#         for labels in _channel_options:
#             _chan_label = ttk.Label(self._sockframe, text=labels)
#             _chan_label.grid(column=col + iters, padx=pax, row=row, pady=pay, sticky=(W, E))
#             iters += 1
#         for chan, vals in _channels.items():
#          _spins = ttk.Spinbox(self._sockframe, from_=0.0, to=300.0, width=width, textvariable=vals[0])
#             _radio = ttk.Radiobutton(self._sockframe, text=chan, variable=vals[1], value=chan.lower())
#             _spins.grid(column=col+2, padx=pax, row=row, pady=pay, sticky=stix)
#             _radio.grid(column=col+3, padx=pax, row=row, pady=pay, sticky=stix)
#
#     # def _configs(self):
#     #     self._configure_mainframe()
#     #     self._configure_userframe()
#     #     self._set_market()
#     #     self._set_channel()
#
#     def _launch_mainloop(self):
#         self._configure_mainframe()
#         self._configure_userframe()
#         self._set_market()
#         self._set_channel()
#         assert self._mains is not None, 'need a mainframe first silly'
#         self.mainloop()
#
#     def run_mainloop(self):
#         self._launch_mainloop()
#
#
# if __name__ == '__main__':
#     ftx_Tk = UserFrame()
#     # print(f'\n>>> dir(ftx_Tk):\n{dir(ftx_Tk)}')
#     ftx_Tk.run_mainloop()


# # import time
# # import random
# # from queue import Queue
# # from threading import Thread, Event
# from tkinter import *
# from tkinter import ttk
# # from collections import defaultdict, Counter
# # from queue import Queue
# # from typing import *
# from pprint import pprint
#
# import logging
# logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s')
#
#
# # class RootMain:
# #     def __init__(self,
# #                  root: Tk = None,
# #                  mainframe: ttk.Frame = None,
# #                  enter_orderbook: StringVar = None,
# #                  enter_trades: StringVar = None,
# #                  enter_tickers: StringVar = None,
# #                  enter_market: StringVar = None,
# #                  ordbk_delay: IntVar = None,
# #                  trade_delay: IntVar = None,
# #                  tick_delay: IntVar = None,
# #                  ):
# #         super().__init__()
# #         self.root = root
# #         self.idle = mainframe
# #         self._enter_market = enter_market
# #         self._enter_orderbook = enter_orderbook
# #         self._enter_trades = enter_trades
# #         self._enter_tickers = enter_tickers
# #         self._ordbk_delay = ordbk_delay
# #         self._trade_delay = trade_delay
# #         self._tick_delay = tick_delay
# #         self._inserts = []
# class RootMain:
#     def __init__(self,
#                  root: Tk = None,
#                  mainframe: ttk.Frame = None,
#                  enter_market: StringVar = None,
#                  check_orderbook: StringVar = None,
#                  check_trades: StringVar = None,
#                  check_tickers: StringVar = None,
#                  ordbk_delay: DoubleVar = None,
#                  trade_delay: DoubleVar = None,
#                  tick_delay: DoubleVar = None,
#                  ):
#         super().__init__()
#         self.root = root
#         self.idle = mainframe
#         self._enter_market = enter_market
#         self._check_orderbook = check_orderbook
#         self._check_trades = check_trades
#         self._check_tickers = check_tickers
#         self._ordbk_delay = ordbk_delay
#         self._trade_delay = trade_delay
#         self._tick_delay = tick_delay
#
#     # def __setitem__(self, key, value):
#     #     logging.debug('>>> CALLED: ')
#     #     self.__dict__[key] = value
#     #
#     # def __getattr__(self, item):
#     #     logging.debug('>>> CALLED: __getattr__')
#     #     return self.__dict__[item]
#     #
#     # def __get__(self, instance, owner):
#     #     logging.debug('>>> CALLED: __get__')
#     #     return self.__dict__[instance]
#     #
#     # def __set__(self, instance, value):
#     #     logging.debug('>>> CALLED: __set__')
#     #     self.__dict__[instance] = value
#     # def __getattr__(self, item):
#     #     return self.__dict__[item]
#     #
#     # def __setattr__(self, key, value):
#     #     self.__dict__[key] = value
#     #
#     # def __get__(self, instance, owner):
#     #     return self.__dict__[instance]
#
#     # def __call__(self, *args, **kwargs):
#     #     return self.__dict__[getattr(args, kwargs)]
#
#     @staticmethod
#     def get_widget_dict(the_widget):
#         ugly = the_widget.configure()
#         for key, val in ugly.items():
#             print(f'\n* {key} *')
#             for v in val:
#                 print(f'\t>>> [ {v} ]')
#
#     def _initialize_idle(self, title='BAWSAQ', padding='6 3 12 12'):
#         assert not self.root, 'RootMain cant be called twice. . .'
#         self.root = Tk()
#         # self.get_widget_dict(self.root)
#         self.root.title(title)
#         self.idle = ttk.Frame(self.root, padding=padding)
#         self.idle.grid(column=0, row=0, sticky=(N, W, E, S))
#         self.root.columnconfigure(0, weight=1)
#         self.root.rowconfigure(0, weight=1)
#         self.root.columnconfigure(3, weight=2)
#         self.root.rowconfigure(1, weight=2)
#         self.idle['borderwidth'] = 2
#
#
# class UserInputFrame(RootMain):
#     _WIDTH = 12
#     _HEIGHT = 10
#     _COL = 0
#     _CSPAN = 2
#     _PADX = 6
#     _ROW = 1
#     _RSPAN = 4
#     _PADY = 6
#     _STIX = (N, W)
#     _MKTS = (
#         'BTC/USD', 'BTC/USDT', 'BTC-PERP', 'BTC/TRYB',
#         'ETH/BTC', 'ETH/USD', 'ETH/USDT', 'ETH-PERP'
#     )
#
#     def __init__(self):
#         super().__init__()
#         self._inserts = []
#
#     def _queue_insert(self):
#         logging.debug('>>> CALLED -> UserInputFrame._queue_insert()')
#         foobar = [('Orderbook', self._check_orderbook),
#                   ('Trades', self._check_trades),
#                   ('Tickers', self._check_tickers)]
#         foob = zip(['Orderbooks', 'Trades', 'Tickers'],
#                    [self._check_orderbook, self._check_trades, self._check_tickers])
#         for foo, bar in list(foob):
#             try:
#                 print(f'>>> {foo} = {bar.get()}')
#             except AttributeError:
#                 pass
#
#         # market, empty = self._enter_market.get(), ['', 0.0, None]
#
#         # stonk = {
#         #     'ordbk': self._check_orderbook.get(),
#         #     'trades': [self._check_trades.get(), self._trade_delay.get()],
#         #     'tickers': [self._check_tickers.get(), self._tick_delay.get()]
#         # }
#         #
#         # if market and stonk['ordbk'] not in empty:
#         #     # self._inserts.append({str(market): stonk['ordbk']})
#         #     # self._inserts.task_done()
#         #     print({str(market): stonk['ordbk']})
#         #     pass
#         # if market and stonk['trades'][0] and stonk['trades'][1] not in empty:
#         #     # self._inserts.append({str(market): (stonk['trades'][0], stonk['trades'][1])})
#         #     # self._inserts.task_done()
#         #     print({str(market): (stonk['trades'][0], stonk['trades'][1])})
#         #     pass
#         # if market and stonk['tickers'][0] and stonk['trades'][1] not in empty:
#         #     # self._inserts.append({str(market): (stonk['trades'][0], stonk['trades'][1])})
#         #     # self._inserts.task_done()
#         #     print({str(market): (stonk['trades'][0], stonk['trades'][1])})
#         #     pass
#
#     @staticmethod
#     def _start_subs():
#         print(f'\n>>> _SUBS.callback(EVENT). . .')
#
#     @staticmethod
#     def _unsub():
#         print('\n\t>>> _UNSUB.callback(EVENT)')
#
#     def _set_states(self):
#         logging.debug('>>> CALLED -> UserInputFrame._set_states()')
#         method_map = (
#             [self._check_orderbook, self._ordbk_delay],
#             [self._check_trades, self._trade_delay],
#             [self._check_tickers, self._tick_delay]
#         )
#         for meth, head in method_map:
#             try:
#                 if meth.get() is not None:
#                     print(f'>>> meth.get({meth.get()}) / head.get({head.get()})')
#             except AttributeError:
#                 pass
#
#     def _organize(self, col=_COL+1, pax=_PADX, cspan=_CSPAN,
#                   row=_ROW, pay=_PADY, rspan=_RSPAN, stix=(N, S)):
#         _splitter = ttk.Separator(self.idle, orient=VERTICAL)
#         _splitter.grid(column=col, padx=pax, rows=row, pady=pay, rowspan=rspan, sticky=stix)
#
#     def _select_market(self, height=_HEIGHT, width=_WIDTH,
#                        col=_COL, pax=_PADX, row=_ROW, pay=_PADY, stix=_STIX):
#         """ Create: MarketLabel -> EntryCombobox -> InsertButton """
#         _market_label = ttk.Label(self.idle, text='-- Market Name --').grid(
#             column=col, padx=pax, row=row, pady=pay, sticky=stix)
#
#         _com = ttk.Combobox(
#             self.idle, height=height, width=width, textvariable=getattr(self, '_enter_market'))
#         _com.grid(column=col+2, padx=pax, row=row, pady=pay, sticky=stix)
#         _com['values'] = self._MKTS
#
#         _butt_insert = ttk.Button(self.idle, text='Insert', width=12, command=self._queue_insert).grid(
#             column=col+4, padx=pax, row=row, pady=pay, sticky=(N, E))
#
#     def _select_channel(self, col=_COL, pax=_PADX, row=_ROW+1, pay=_PADY,
#                         stix=_STIX, iters=2):
#         """ Create: ChannelLabel -> ChannelCheckbutton """
#         _chan_label = ttk.Label(self.idle, text='-- Channel Type --').grid(
#             column=col, padx=pax + 6, row=row, pady=pay, sticky=stix)
#         self._check_orderbook = StringVar(self.idle, value='orderbook', name='Orderbook')
#         self._check_trades = StringVar(self.idle, value='trades', name='Trades')
#         self._check_tickers = StringVar(self.idle, value='tickers', name='Tickers')
#         string_variables = (self._check_orderbook, self._check_trades, self._check_tickers)
#         for str_var in string_variables:
#             _select_chan = ttk.Checkbutton(
#                 self.idle, text=str_var, command=None, variable=str_var,
#                 onvalue=str_var.get(), offvalue=None)
#             _select_chan.grid(column=col+iters, padx=pax, row=row, pady=pay, sticky=stix)
#             _select_chan.state(['!disabled', '!selected'])
#             iters += 1
#
#     def _select_delays(self, col=_COL, cspan=_CSPAN, pax=_PADX,
#                        row=_ROW+2, pay=_PADY, stix=_STIX, inc=2):
#         _delay_label = ttk.Label(self.idle, text='-- Delay Interval --').grid(
#             column=col, columnspan=cspan, padx=pax, row=row, pady=pay, sticky=stix)
#         for delay in [self._ordbk_delay, self._trade_delay, self._tick_delay]:
#             _delays = ttk.Spinbox(self.idle, from_=0.0, to=360.0, width=12, textvariable=delay)
#             _delays.grid(column=col + inc, padx=pax, row=row, pady=pay, sticky=stix)
#             inc += 1
#             _delays.state(['disabled'])
#
#     def _select_buttons(self, width=_WIDTH, col=_COL+3, cspan=_CSPAN, pax=_PADX,
#                         row=_ROW+4, pay=_PADY, stix=_STIX, iters=0):
#         """ Configures _do_some_action buttons """
#         wrap_buttons = [('Subscribe', self._start_subs), ('Unsubscribe', self._unsub)]
#         for button, action in wrap_buttons:
#             _adding = ttk.Button(self.idle, text=button, width=width, command=action)
#           _adding.grid(column=col + iters, padx=pax, columnspan=cspan, row=row, pady=pay, sticky=stix)
#             iters += 1
#
#     def _create_userframe(self):
#         self._initialize_idle()
#         self._organize()
#         self._select_market()
#         self._select_channel()
#         self._select_delays()
#         self._select_buttons()
#
#     def _launch_mainloop(self):
#         if self.root is None:
#             self._create_userframe()
#         assert self.root and self.idle is not None, '_root is deader than fuck moron'
#         self.root.mainloop()
#
#     def launch_mainloop(self):
#         self._launch_mainloop()
#
# if __name__ == '__main__':
#     # print(dir(UserInputFrame))
#     ftx01 = UserInputFrame()
#     ftx01.launch_mainloop()
#
# # self._btn_insert = btn_insert  # Insert object into [format] queue for many subs
# # self._btn_sub = btn_sub  # If fifo & !entry None: single_sub else: batch_sub
# # self._btn_unsub = btn_unsub  # Select from subs_menu, unsub on click
# # menu_subbing: ttk.Menu = None,        # Dynamically add inserts to sub to
# # menu_subbed: ttk.Menu = None          # Dynamically add successful subscriptions
#
# # sets_ordbk: StringVar = None,
# # sets_trades: StringVar = None,
# # sets_tickers: StringVar = None,
# # entry_orderbook: ttk.Checkbutton = None,
# # entry_trades: ttk.Checkbutton = None,
# # entry_tickers: ttk.Checkbutton = None,
# #
# # entry_market: ttk.Entry = None,
# # entry_delay: ttk.Entry = None,
# #
# # btn_insert: ttk.Button = None,
# # btn_sub: ttk.Button = None,
# # btn_unsub: ttk.Button = None
#
# # self._combo_channel = ttk.Combobox(self.idle, width=12, textvariable=self._got_channel)
# # self._combo_channel.grid(column=2, row=2, sticky=(W, E))
# # self._combo_channel['values'] = ('orderbook', 'tickers', 'trades')
# # self._combo_channel.state(['readonly'])
#
# # self._streams: DefaultDict[str, Tuple[str, float]] = defaultdict()
# # def __setitem__(self, key, value):
# #     self.__dict__['_streams'][key] = value
#
# # def _configure_buttons(self):
# #     self._insert = ttk.Button(self._mf, text='Insert-to-Queue',
# #                               command=self._user_entries()
# #                               ).grid(column=3, row=3, sticky=(W, ))
# #     self._start_pool = ttk.Button(self._mf, text='Open-WebSocket',
# #                                   command=self._open_websocket()
# #                                   ).grid(column=3, row=3, sticky=(W, ))
#
# # def win_event_loop(self):
# #     _run_event = Event()
# #     _run_event.set()
# #     self._configure_labels()
# #     # self._configure_buttons()
# #     entries_thread = Thread(name='_ENTRIES', target=self._configure_entries, args=(_run_event,))
# #     entries_thread.start()
# #     self.root.mainloop()
#
# # def _user_entries(self, *args):
# #     (channel, market, delay) = args
# #     # {'channel': ('market', float), 'trades': ('BTC-PERP', 2.0), ...}
# #     self._streams[channel] = (market, delay)
# #     # print(self._streams)
# #
# # def _open_websocket(self):
# #     print('_open_foobar')
# #     for x, y in self._streams.items():
# #         print(x, y)
# #         foo = ttk.Label(self._idle, text='(Key={x} -> Value={y})').grid()
#
#
# # ttt = ['-- Channel Type --', '-- Market Name --', '-- Poll Interval --']
# # g = {'Col': 1, 'Cspan': 2, 'pX': 3, 'Row': 2}
# # _label_channel = ttk.Label(self.idle, text=ttt[0]).grid(
# #     column=g['Col'], columnspan=g['Cspan'], padx=g['pX'], row=g['Row'], sticky=(N, W))
# # _label_market = ttk.Label(self.idle, text=ttt[1]).grid(
# #     column=g['Col'], columnspan=g['Cspan'], padx=g['pX'], row=g['Row'] + 1, sticky=(N, W))
# # _label_delay = ttk.Label(self.idle, text=ttt[2]).grid(
# #     column=g['Col'], columnspan=g['Cspan'], padx=g['pX'], row=g['Row'] + 2, sticky=(N, W))
# # channels = {
# #     'Orderbooks': [self._enter_orderbook, 'orderbook'],
# #     'Trades': [self._enter_trades, 'trades'],
# #     'Tickers': [self._enter_tickers, 'tickers']
# # }
# # grids = {'Col': 3, 'Row': 2, 'sticky': (W, E), 'Iters': 0}
# # _select_ordbk = ttk.Checkbutton(
# #     self.idle, text='Orderbooks', command=self._set_vars, variable=self._enter_orderbook,
# #     onvalue='orderbook', offvalue='None')
# # _select_trades = ttk.Checkbutton(
# #     self.idle, text='Trades', command=self._set_vars, variable=self._enter_trades,
# #     onvalue='trades', offvalue='None')
# # _select_tickers = ttk.Checkbutton(
# #     self.idle, text='Tickers', command=self._set_vars, variable=self._enter_tickers,
# #     onvalue='tickers', offvalue='None')
# # _select_ordbk.grid(column=grids['Col'], row=grids['Row'], sticky=grids['sticky'])
# # _select_trades.grid(column=grids['Col']+1, row=grids['Row'], sticky=grids['sticky'])
# # _select_tickers.grid(column=grids['Col']+2, row=grids['Row'], sticky=grids['sticky'])

# from tkinter import *
# from tkinter import ttk
# import logging
#
# logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s')
#
#
# class RootsMain(Tk):
#     def __init__(self,
#                  userframe: Frame = None,
#                  streamframe: Frame = None,
#                  market_str: StringVar = None,
#                  spin_ordbk_dub: DoubleVar = None,
#                  spin_trades_dub: DoubleVar = None,
#                  spin_tickers_dub: DoubleVar = None,
#                  radio_ordbk_bool: BooleanVar = None,
#                  radio_trades_bool: BooleanVar = None,
#                  radio_tickers_bool: BooleanVar = None):
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
#         logging.debug(f'>>> ({key}, {value})')
#         self.__dict__[key] = value
#
#     def _configure_mainframe(self, border_width: int = 5, stix: tuple = (N, W, E, S)):
#         self.title('Stream Wizard')
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
#         self._sockframe = ttk.Frame(self._mains, padding='3 3 12 12')
#         self._market_str = StringVar(self._mains)
#         self._spin_ordbk_dub = DoubleVar(self._mains)
#         self._spin_trades_dub = DoubleVar(self._mains)
#         self._spin_tickers = DoubleVar(self._mains)
#         self._radio_ordbk = BooleanVar(self._mains)
#         self._radio_trades = BooleanVar(self._mains)
#         self._radio_tickers = BooleanVar(self._mains)
#         self._button_helper = [
#             ('Insert', self._queued), ('Subscribe', self._subs), ('Unsubscribe', self._unsub)]
#           # self._configure_userframe()
# # self._configure_dataframe()
# # market_str: StringVar = None,
# # spin_ordbk_dub: DoubleVar = None,
# # spin_trades_dub: DoubleVar = None,
# # spin_tickers_dub: DoubleVar = None,
# # radio_ordbk_bool: BooleanVar = None,
# # radio_trades_bool: BooleanVar = None,
# # radio_tickers_bool: BooleanVar = None):
# # self._market_str = market_str
# # self._spin_ordbk_dub = spin_ordbk_dub
# # self._spin_trades_dub = spin_trades_dub
# # self._spin_tickers = spin_tickers_dub
# # self._radio_ordbk = radio_ordbk_bool
# # self._radio_trades = radio_trades_bool
# # self._radio_tickers = radio_tickers_bool
#
#     def _configure_userframe(self, border=5, stix=(N, W, E, S)):
#         self._configure_mainframe()
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
#         _mkt_sep = ttk.Separator(self._sockframe, orient=HORIZONTAL).grid(
#             column=0, columnspan=5, padx=pax, row=2, pady=pay, sticky=(W, E))
#         _combo["values"] = markets
#
# if __name__ == '__main__':
#     ftx_Tk = UserFrame()
#     # print(f'\n>>> dir(ftx_Tk):\n{dir(ftx_Tk)}')
#     ftx_Tk.launch_mainloop()

# def _configure_mains(self, border: int = 5, stix: tuple = (N, W, E, S)):
#     self._mains = ttk.Frame(self.winfo_toplevel(), padding='3 3 12 12')
#     self._mains.grid(column=0, row=0, sticky=stix)
#     self._mains.configure(borderwidth=border)
#     self._mains.columnconfigure(0, weight=1)
#     self._mains.columnconfigure(1, weight=1)
#     self._mains.rowconfigure(0, weight=1)
#     self._mains.rowconfigure(1, weight=2)

# def _configure_userframe(self, border: int = 2, stix: tuple = (N, W)):
#     self._sockframe = ttk.Frame(self._mains, padding='3 3 12 12')
#     self._sockframe.grid(column=0, row=0, sticky=stix)
#     self._sockframe.configure(borderwidth=border, relief='raised')
#     self._sockframe.columnconfigure(0,  minsize=100, weight=1)
#     self._sockframe.columnconfigure(1, minsize=100, weight=1)
#     self._sockframe.columnconfigure(2, weight=2)
#     self._sockframe.rowconfigure(0, weight=1)
#
# def _configure_dataframe(self, border: int = 2, stix: tuple = (N, E)):
#     self._dataframe = ttk.Frame(self._mains, padding='12 12 3 3')
#     self._dataframe.grid(column=1, row=0, rowspan=6, sticky=stix)
#     self._dataframe.configure(borderwidth=border, relief='raised')
#     self._dataframe.columnconfigure(0, weight=1)
#     self._dataframe.rowconfigure(0, weight=1)

# def _frame_manager(self, pax=2, pay=2, stix=(N, S, W, E)):
#     self.title('Medium Rare Hot Dog')
#     self.winfo_toplevel().columnconfigure(0, minsize=400, weight=1)
#     self.winfo_toplevel().rowconfigure(0, minsize=250, weight=1)
# self._sockframe = ttk.Labelframe(self._mains, padding=pad)
# self._dataframe = ttk.LabelFrame(self._mains, padding=pad)
#
#     def _set_channel(self, col=_COL, pax=_PADX, row=_ROW+2, pay=_PADY, width=_WIDE, stix=_STIX, iters=1):
#         _channels = {'Orderbook': [self._spin_ordbk_dub, self._radio_ordbk],
#                      'Trades': [self._spin_trades_dub, self._radio_trades],
#                      'Tickers': [self._spin_tickers, self._radio_tickers]}
#         _op_label = ttk.Label(self._sockframe, text='--Select Channels --').grid(
#                 column=0, padx=pax, row=row, pady=pay, sticky=stix)
#         _delay_label = ttk.Label(self._sockframe, text='-- Set Delay --').grid(
#             column=2, padx=pax+3, row=row, pady=pay, sticky=stix)
#
#         for chan, vals in _channels.items():
#             _spins = ttk.Spinbox(self._sockframe, from_=0.0, to=300.0, width=width, textvariable=vals[0])
#             _radio = ttk.Radiobutton(self._sockframe, text=chan, variable=vals[1], value=chan.lower())
#             _spins.grid(column=col+2, padx=pax+1, row=row+iters, pady=pay, sticky=stix)
#             _radio.grid(column=col, padx=pax+4, row=row+iters, pady=pay, sticky=stix)
#             _radio.state(['!disabled', '!selected'])
#             iters += 1
#
#         _chan_sep = ttk.Separator(self._sockframe, orient=HORIZONTAL).grid(
#             column=0, columnspan=5, padx=pax, row=row + iters, pady=pay+3, sticky=(W, E))
#
#     def _set_buttons(self, width=_WIDE, col=_COL, pax=_PADX, row=_ROW+7, pay=_PADY, stix=_STIX, iters=0):
#         for btn, action in self._button_helper:
#             _queued = ttk.Button(
#                 self._sockframe, text=btn, width=width, command=action).grid(
#                 column=col+iters, padx=pax, row=row, pady=pay, sticky=stix)
#             iters += 1
#
#     def _queued(self):
#         try:
#             print(f'\n>>> cocksucker activated, {self._market_str.get()}')
#         except AttributeError as e:
#             print(e)
#
#     def _subs(self):
#         try:
#             print(f'\n>>> THE BIG COCKSUCKER: '
#                   f'\n>>> {self._market_str.get()}'
#                   f'\n>>> {self._spin_ordbk_dub}, {self._radio_ordbk}'
#                   f'\n>>> {self._spin_trades_dub}, {self._radio_trades}'
#                   f'\n>>> {self._spin_tickers}, {self._radio_tickers}')
#         except AttributeError as e:
#             print(e)
#
#     def _unsub(self):
#         try:
#             print(f'\n>>> THE BIG COCKSUCKER: '
#                   f'\n>>> {self._market_str.get()}'
#                   f'\n>>> {self._spin_ordbk_dub}, {self._radio_ordbk}'
#                   f'\n>>> {self._spin_trades_dub}, {self._radio_trades}'
#                   f'\n>>> {self._spin_tickers}, {self._radio_tickers}')
#         except AttributeError as e:
#             print(e)
#
#     def _launch_mainloop(self):
#         self._configure_mainframe()
#         self._configure_userframe()
#         self._set_market()
#         self._set_channel()
#         self._set_buttons()
#         assert self._mains is not None, 'need a mainframe first silly'
#         self.mainloop()
#
#     def launch_mainloop(self):
#         self._launch_mainloop()
#
#


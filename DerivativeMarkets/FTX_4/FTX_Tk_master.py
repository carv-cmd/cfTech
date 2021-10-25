# from tkinter import *
# from tkinter import ttk
# from typing import Any, List
#
# import logging
# logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s')
#
#
# class RootsMain(Tk):
#     """ TODO: Exception raised by most tk errors is tk.TclError """
#     _wConfig = {'borderwidth': 5, 'relief': 'raised'}
#     _LfConfig = {'sock': 'WebSocket-API', 'rest': 'REST-API', 'data': 'DataFrame'}
#     _fPads = '3 3 12 12'
#
#     def __init__(self):
#         super().__init__()
#         self._mains = ttk.Frame(self.winfo_toplevel(), padding=self._fPads)
#         self._sockframe = ttk.Labelframe(self._mains, padding=self._fPads)
#         self._restframe = ttk.LabelFrame(self._mains, padding=self._fPads)
#         self._dataframe = ttk.LabelFrame(self._mains, padding=self._fPads)
#         self._ui_frames()
#         # self._configure_userframe()
#         # self._configure_dataframe()
#         # market_str: StringVar = None,
#         # spin_ordbk_dub: DoubleVar = None,
#         # spin_trades_dub: DoubleVar = None,
#         # spin_tickers_dub: DoubleVar = None,
#         # radio_ordbk_bool: BooleanVar = None,
#         # radio_trades_bool: BooleanVar = None,
#         # radio_tickers_bool: BooleanVar = None):
#         # self._market_str = market_str
#         # self._spin_ordbk_dub = spin_ordbk_dub
#         # self._spin_trades_dub = spin_trades_dub
#         # self._spin_tickers = spin_tickers_dub
#         # self._radio_ordbk = radio_ordbk_bool
#         # self._radio_trades = radio_trades_bool
#         # self._radio_tickers = radio_tickers_bool
#     # def _configure_mains(self, border: int = 5, stix: tuple = (N, W, E, S)):
#     #     self._mains = ttk.Frame(self.winfo_toplevel(), padding='3 3 12 12')
#     #     self._mains.grid(column=0, row=0, sticky=stix)
#     #     self._mains.configure(borderwidth=border)
#     #     self._mains.columnconfigure(0, weight=1)
#     #     self._mains.columnconfigure(1, weight=1)
#     #     self._mains.rowconfigure(0, weight=1)
#     #     self._mains.rowconfigure(1, weight=2)
#
#     # def _configure_userframe(self, border: int = 2, stix: tuple = (N, W)):
#     #     self._sockframe = ttk.Frame(self._mains, padding='3 3 12 12')
#     #     self._sockframe.grid(column=0, row=0, sticky=stix)
#     #     self._sockframe.configure(borderwidth=border, relief='raised')
#     #     self._sockframe.columnconfigure(0,  minsize=100, weight=1)
#     #     self._sockframe.columnconfigure(1, minsize=100, weight=1)
#     #     self._sockframe.columnconfigure(2, weight=2)
#     #     self._sockframe.rowconfigure(0, weight=1)
#     #
#     # def _configure_dataframe(self, border: int = 2, stix: tuple = (N, E)):
#     #     self._dataframe = ttk.Frame(self._mains, padding='12 12 3 3')
#     #     self._dataframe.grid(column=1, row=0, rowspan=6, sticky=stix)
#     #     self._dataframe.configure(borderwidth=border, relief='raised')
#     #     self._dataframe.columnconfigure(0, weight=1)
#     #     self._dataframe.rowconfigure(0, weight=1)
#
#     # def _frame_manager(self, pax=2, pay=2, stix=(N, S, W, E)):
#     #     self.title('Medium Rare Hot Dog')
#     #     self.winfo_toplevel().columnconfigure(0, minsize=400, weight=1)
#     #     self.winfo_toplevel().rowconfigure(0, minsize=250, weight=1)
#     # self._sockframe = ttk.Labelframe(self._mains, padding=pad)
#     # self._dataframe = ttk.LabelFrame(self._mains, padding=pad)
#     def __setattr__(self, key, value):
#         self.__dict__[key] = value
#
#     def _ui_frames(self, pax=2, pay=2, stix=(N, S, W, E)):
#         self.title('Medium Rare Hot Dog')
#         self.winfo_toplevel().columnconfigure(0, minsize=400, weight=1)
#         self.winfo_toplevel().rowconfigure(0, minsize=250, weight=1)
#         self._frame_config(self._mains, col=0, padx=pax, row=0, pady=pay, stix=stix,
#                            row_col=[(1, 1), (1, 1)], mins=200, **self._wConfig)
#         self._frame_config(self._sockframe, col=0, padx=pax, row=0, pady=pay, stix=NW,
#                            row_col=[(1, 1), (2, 1)], mins=100, text=self._LfConfig['sock'])
#         self._frame_config(self._restframe, col=1, padx=pax, row=0, pady=pay, stix=NE,
#                            row_col=[(1, 1)], mins=100, text=self._LfConfig['data'])
#         self._frame_config(self._dataframe, col=0, padx=pax, row=1, pady=pay, stix=SW,
#                            row_col=[(1, 1)], mins=100, text=self._LfConfig['sock'])
#
#     @staticmethod
#     def _frame_config(frame, col: int, padx: int, row: int, pady: int, stix: tuple,
#                       row_col: list, mins: int = 300, cspan=1, rspan=1, text=None, **kwargs):
#         logging.debug(f'>>> _frame_config -> type: {type(frame)}')
#         frame.grid(column=col, columnspan=cspan, padx=padx,
#                    row=row, rowspan=rspan, pady=pady, sticky=stix)
#         for index in range(len(row_col)):
#             frame.columnconfigure(index, minsize=mins, weight=row_col[index][0])
#             frame.rowconfigure(index, minsize=mins*0.4,  weight=row_col[index][1])
#         if type(frame) is ttk.LabelFrame:
#             frame.configure(text=text)
#         else:
#             frame.configure(kwargs)
#
#     @staticmethod
#     def _get_separator(frame, orient: Any, column: int, cspan: int, padx: int,
#                        row: int, rspan: int, pady: int, stix: Any):
#         _mkt_separator = ttk.Separator(frame, orient=orient).grid(
#             column=column, columnspan=cspan, padx=padx,
#             row=row, pady=pady, rowspan=rspan, sticky=stix)
#
#     @staticmethod
#     def _get_label(frame, text: str, column: int, padx: int,
#                    row: int, pady: int, stix: Any):
#         _label = ttk.Label(frame, text=text).grid(
#             column=column, padx=padx, row=row, pady=pady, sticky=stix)
#
#     @staticmethod
#     def _get_combo(frame, markets: tuple, strvar: StringVar, width: int, height: int,
#                    column: int, padx: int, row: int, pady: int, stix: Any):
#         _combo = ttk.Combobox(frame, height=height, width=width, textvariable=strvar)
#         _combo.grid(column=column, padx=padx, row=row, pady=pady, sticky=stix)
#         _combo["values"] = markets
#
#     @staticmethod
#     def _get_spinbox(frame, width: int, txtvar: StringVar, low: float, high: float,
#                      column: int, padx: int, row: int, pady: int, stix: Any):
#         _spins = ttk.Spinbox(frame, from_=low, to=high, width=width, textvariable=txtvar)
#         _spins.grid(column=column, padx=padx, row=row, pady=pady, sticky=stix)
#
#     @staticmethod
#     def _get_radiobutton(frame, text: str, variable: StringVar, value: Any,
#                          column: int, padx: int, row: int, pady: int, stix: Any):
#         _radio = ttk.Radiobutton(frame, text=text, variable=variable, value=value.lower())
#         _radio.grid(column=column, padx=padx, row=row, pady=pady, sticky=stix)
#         _radio.bind('<Activate>', _radio.state(['!disabled', 'selected']))
#         _radio.bind('<ButtonPress-1> <Deactivate>', _radio.state(['!selected']))
#
#     @staticmethod
#     def _get_button(frame, text: str, cmd: Any, width: int,
#                     column: int, padx: int, row: int, pady: int, stix: Any):
#         _insert = ttk.Button(frame, text=text, width=width, command=cmd).grid(
#             column=column, padx=padx, row=row, pady=pady, sticky=stix)
#
#     @staticmethod
#     def inspect_widget(_frames: Frame):
#         logging.debug(f'>>> newFrame.grid_slaves = {_frames.grid_slaves()}')
#         logging.debug(f'>>> newFrame.grid_size = {_frames.grid_size()}')

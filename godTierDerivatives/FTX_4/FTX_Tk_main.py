# import time
# import random
# from queue import Queue
from threading import Thread, Event
from tkinter import *
from tkinter import ttk
from collections import defaultdict, Counter
from queue import Queue
from typing import *


# import logging
# logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s')


class RootMain:
    def __init__(self, root: Tk = None, mainframe: ttk.Frame = None):
        super().__init__()
        self.root = root
        self.idle = mainframe

    def _initialize_idle(self):
        assert not self.root, 'RootMain cant be called twice. . .'
        self.root = Tk()
        self.root.title('BALL_SACK')
        self.idle = ttk.Frame(self.root, padding='3 3 12 12')
        self.idle.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)


class UserInputFrame(RootMain):
    def __init__(self,
                 ordbk_var: StringVar = None,
                 trades_var: StringVar = None,
                 ticker_var: StringVar = None,
                 market_var: StringVar = None,
                 trade_delay: DoubleVar = None,
                 tick_delay: DoubleVar = None,
                 # inserts: Queue = None
                 ):
        super().__init__()
        self._enter_orderbook = ordbk_var
        self._enter_trades = trades_var
        self._enter_tickers = ticker_var
        self._enter_market = market_var  # Use 're(C++)' validation -> StringVar()
        self._trade_delay = trade_delay
        self._tick_delay = tick_delay
        self._inserts = []

    def __setitem__(self, key, value):
        self.__dict__['_inserts'][key] = value

    def _set_channel(self):
        pass

    def _configure_labels(self, col: int = 1, cspan: int = 2, px: int = 3, row: int = 1):
        texts = ['-- Market Name --', '-- Channel Type --', '-- Poll Interval --']
        for txt in range(len(texts)):
            _make_label = ttk.Label(self.idle, text=texts[txt]).grid(
                column=col, columnspan=cspan, padx=px,
                row=row + txt, rowspan=1, sticky=(N, W))

    def _config_channels(self, col: int = 3, row: int = 2, iters: int = 0):
        """ Configures ChannelType checkboxes """
        self._enter_orderbook, self._enter_trades, self._enter_tickers = \
            StringVar(), StringVar(), StringVar()
        channels = {'Orderbooks': [self._enter_orderbook, 'orderbook'],
                    'Trades': [self._enter_trades, 'trades'],
                    'Tickers': [self._enter_tickers, 'tickers']}
        for channel, data in channels.items():
            _selects = ttk.Checkbutton(
                self.idle, text=channel, command=self._set_channel,
                variable=data[0], onvalue=data[1], offvalue=None)
            _selects.grid(column=col + iters, row=row, sticky=(W, E))
            iters += 1

    def _config_forms(self, col: int = 3, width: int = 12, stik=(W, E)):
        """ Configures _mkt_delay_entry boxes """
        self._enter_market, self._trade_delay, self._tick_delay = StringVar(), DoubleVar(), DoubleVar()
        entries, cols, rows = [self._enter_market, self._trade_delay, self._tick_delay], \
                              [3, 3, 4], [1, 3, 3]
        for _entry, _cols, _rows in list(zip(entries, cols, rows)):
            print(_entry.get(), _cols, _rows)
            _txt = ttk.Entry(self.idle, width=width, textvariable=_entry)
            _txt.grid(column=_cols, columnspan=1, row=_rows, sticky=stik)

    def _config_insert(self):
        """ Configures _do_some_action buttons """
        tk_insertion = ttk.Button(self.idle, text='Insert-Subs', width=20, command=self._put_inserts)
        tk_subscribe = ttk.Button(self.idle, text='Sub Stream(s)', width=20, command=self._subs)
        tk_unsubscribe = ttk.Button(self.idle, text='Unsub Streams(s)', width=20, command=self._unsub)
        tk_insertion.grid(column=0, columnspan=2, row=6, sticky=(S, E))
        tk_subscribe.grid(column=1, row=7, sticky=(S, E))
        tk_unsubscribe.grid(column=1, row=8, sticky=(S, E))
        splits = ttk.Separator(self.idle, orient=HORIZONTAL)
        splits.grid(column=0, row=5, sticky=(N, S))

    def _put_inserts(self):
        market, empty = self._enter_market.get(), ['', 0.0, None]
        stonk = {
            'ordbk': self._enter_orderbook.get(),
            'trades': [self._enter_trades.get(), self._trade_delay.get()],
            'tickers': [self._enter_tickers.get(), self._tick_delay.get()]
        }
        if market and stonk['ordbk'] not in empty:
            self._inserts.append({str(market): stonk['ordbk']})
            pass
            # self._inserts.task_done()
        if market and stonk['trades'][0] and stonk['trades'][1] not in empty:
            self._inserts.append({str(market): (stonk['trades'][0], stonk['trades'][1])})
            pass
            # self._inserts.task_done()
        if market and stonk['tickers'][0] and stonk['trades'][1] not in empty:
            self._inserts.append({str(market): (stonk['trades'][0], stonk['trades'][1])})
            pass
            # self._inserts.task_done()
        try:
            print(self._inserts.pop())
        except IndexError:
            pass

    def _subs(self):
        print(f'Generated Insert: {self._inserts.pop()})')
        # while True:
        #     print(f'_handle_subs({self._inserts.get()})')

    @staticmethod
    def _unsub():
        # raise NotImplementedError()
        print('_handle_unsub.method')

    def _create_userframe(self):
        self._initialize_idle()
        self._configure_labels()
        self._config_forms()
        self._config_channels()
        self._config_insert()

    def _root_mainloop(self):
        if self.root is None:
            self._create_userframe()
        assert self.root and self.idle is not None, '_root is deader than fuck moron'
        insert_thread = Thread(name='_INSERTS', target=self._put_inserts)
        subs_thread = Thread(name='_SUBS', target=self._subs)
        insert_thread.start()
        subs_thread.start()
        self.root.mainloop()

    def run_mainloop(self):
        self._root_mainloop()


if __name__ == '__main__':
    ftx01 = UserInputFrame()
    ftx01.run_mainloop()

# self._btn_insert = btn_insert  # Insert object into [format] queue for many subs
# self._btn_sub = btn_sub  # If fifo & !entry None: single_sub else: batch_sub
# self._btn_unsub = btn_unsub  # Select from subs_menu, unsub on click
# menu_subbing: ttk.Menu = None,        # Dynamically add inserts to sub to
# menu_subbed: ttk.Menu = None          # Dynamically add successful subscriptions


# sets_ordbk: StringVar = None,
# sets_trades: StringVar = None,
# sets_tickers: StringVar = None,
# entry_orderbook: ttk.Checkbutton = None,
# entry_trades: ttk.Checkbutton = None,
# entry_tickers: ttk.Checkbutton = None,
#
# entry_market: ttk.Entry = None,
# entry_delay: ttk.Entry = None,
#
# btn_insert: ttk.Button = None,
# btn_sub: ttk.Button = None,
# btn_unsub: ttk.Button = None

# self._combo_channel = ttk.Combobox(self.idle, width=12, textvariable=self._got_channel)
# self._combo_channel.grid(column=2, row=2, sticky=(W, E))
# self._combo_channel['values'] = ('orderbook', 'tickers', 'trades')
# self._combo_channel.state(['readonly'])

# self._streams: DefaultDict[str, Tuple[str, float]] = defaultdict()
# def __setitem__(self, key, value):
#     self.__dict__['_streams'][key] = value

# def _configure_buttons(self):
#     self._insert = ttk.Button(self._mf, text='Insert-to-Queue',
#                               command=self._user_entries()
#                               ).grid(column=3, row=3, sticky=(W, ))
#     self._start_pool = ttk.Button(self._mf, text='Open-WebSocket',
#                                   command=self._open_websocket()
#                                   ).grid(column=3, row=3, sticky=(W, ))

# def win_event_loop(self):
#     _run_event = Event()
#     _run_event.set()
#     self._configure_labels()
#     # self._configure_buttons()
#     entries_thread = Thread(name='_ENTRIES', target=self._configure_entries, args=(_run_event,))
#     entries_thread.start()
#     self.root.mainloop()

# def _user_entries(self, *args):
#     (channel, market, delay) = args
#     # {'channel': ('market', float), 'trades': ('BTC-PERP', 2.0), ...}
#     self._streams[channel] = (market, delay)
#     # print(self._streams)
#
# def _open_websocket(self):
#     print('_open_foobar')
#     for x, y in self._streams.items():
#         print(x, y)
#         foo = ttk.Label(self._idle, text='(Key={x} -> Value={y})').grid()


# ttt = ['-- Channel Type --', '-- Market Name --', '-- Poll Interval --']
# g = {'Col': 1, 'Cspan': 2, 'pX': 3, 'Row': 2}
# _label_channel = ttk.Label(self.idle, text=ttt[0]).grid(
#     column=g['Col'], columnspan=g['Cspan'], padx=g['pX'], row=g['Row'], sticky=(N, W))
# _label_market = ttk.Label(self.idle, text=ttt[1]).grid(
#     column=g['Col'], columnspan=g['Cspan'], padx=g['pX'], row=g['Row'] + 1, sticky=(N, W))
# _label_delay = ttk.Label(self.idle, text=ttt[2]).grid(
#     column=g['Col'], columnspan=g['Cspan'], padx=g['pX'], row=g['Row'] + 2, sticky=(N, W))
# channels = {
#     'Orderbooks': [self._enter_orderbook, 'orderbook'],
#     'Trades': [self._enter_trades, 'trades'],
#     'Tickers': [self._enter_tickers, 'tickers']
# }
# grids = {'Col': 3, 'Row': 2, 'sticky': (W, E), 'Iters': 0}
# _select_ordbk = ttk.Checkbutton(
#     self.idle, text='Orderbooks', command=self._set_vars, variable=self._enter_orderbook,
#     onvalue='orderbook', offvalue='None')
# _select_trades = ttk.Checkbutton(
#     self.idle, text='Trades', command=self._set_vars, variable=self._enter_trades,
#     onvalue='trades', offvalue='None')
# _select_tickers = ttk.Checkbutton(
#     self.idle, text='Tickers', command=self._set_vars, variable=self._enter_tickers,
#     onvalue='tickers', offvalue='None')
# _select_ordbk.grid(column=grids['Col'], row=grids['Row'], sticky=grids['sticky'])
# _select_trades.grid(column=grids['Col']+1, row=grids['Row'], sticky=grids['sticky'])
# _select_tickers.grid(column=grids['Col']+2, row=grids['Row'], sticky=grids['sticky'])
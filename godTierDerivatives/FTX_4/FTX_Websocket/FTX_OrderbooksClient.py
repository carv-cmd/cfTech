# from ftx_only_orderbook import FtxWebsocketClient, logging, Thread, Event
# from gevent import socket
# import greenlet
# from threading import activeCount as activeCountThreads
from threading import enumerate as enumerate_threads
from queue import Queue
from _queue import Empty
from FTX_Orderbooks import *


class ClientSocket(FtxWebsocketClient):
    """
    Create class instance and pass tuple with market names to .heavy_wizard()
    Socket is opened with exchange server, subscription requests sent
    Efficient wait loop for orderbook updates implemented with gevent.Event
    """
    def __init__(self):
        """ All attributes _protected to protect proper synchronization pattern """
        super().__init__()
        self._subs_pool = Queue()
        self._write_pool = Queue()
        self._run_event = Event()
        self._thread_pooler = None

    @staticmethod
    def get_local_ts():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    def _write_worker(self) -> Any:
        """
        TODO raise NotImplementedError() -> inherit attributes to database_handler
        Processes queued items for safe-writes to file.txt
        """
        try:
            while True:
                (market, update, update_ts, channel) = self._write_pool.get(timeout=5)
                valid_name = ''.join(['_' if x in '/' else x for x in market]).upper()
                with open(file=f'../temp_storage/{valid_name}_{channel}.txt', mode='a+') as filer:
                    filer.writelines(f'UPDATED_TS: {update_ts}\nDATA_SAMPLE: {update}\n')
                    self._write_pool.task_done()
        except Empty:
            logging.debug(f'* SafeWriteQueue.isEmpty(joinQueue=True) *')
        except OSError as ose:
            raise ose
        finally:
            self._write_pool.join()

    def _ordbk_task(self, market: str, delay: float = 1.0) -> None:
        """ Upon update, object FIFO-Queued for safe writes. """
        logging.debug(f'<<< _ORDER_BOOK_TASK({market}, delay=wait()).started(protected) >>>')
        while self._run_event.is_set():
            (mkt_ordbk, ordbk_ts) = self.get_orderbook(market=market), self.get_ordbk_ts(market=market)
            self._write_pool.put([market, mkt_ordbk, ordbk_ts, 'ORDERBOOK'])
            logging.debug(f'-> Orderbook({market}).recv[ <{ordbk_ts}> ]')
            time.sleep(delay)
            self.wait_for_orderbook_update(market=market, timeout=5.0)

    def _tick_task(self, market: str, delay: float = 4) -> None:
        logging.debug(f'>>> _TICKERS_TASK(market={market}, delay={delay})')
        while self._run_event.is_set():
            (mkt_ticks, tick_ts) = self.get_tickers(market=market), self.get_ticker_ts(market=market)
            if len(mkt_ticks) > 0:
                self._write_pool.put([market, mkt_ticks, tick_ts, 'TICKERS'])
                logging.debug(f'>>> Tickers({market}).recv[<{tick_ts}>]')
                time.sleep(delay)

    def _trade_task(self, market: str, delay: float = 2) -> None:
        logging.debug(f'>>> _TRADES_TASK(market={market}, delay={delay})')
        while self._run_event.is_set():
            (mkt_trades, local_ts) = self.get_trades(market=market), self.get_local_ts()
            if len(mkt_trades) > 0:
                self._write_pool.put([market, mkt_trades, local_ts, 'TRADES'])
                logging.debug(f'>>> Tickers({market}).recv[<{local_ts}>]')
                time.sleep(delay)

    def _stream_pooler(self, streamers):
        """ Creates thread tasked with polling XYZ market, FIFO.put for processing """
        pools = {'orderbook': self._ordbk_task, 'tickers': self._tick_task, 'trades': self._trade_task}
        for channel, subs in streamers.items():
            for market in subs[1]:
                logging.debug(f'>>> _QUEUED_STARTS: [ {channel}_{market}, delay={subs[0]} ]')
                mkt_threader = Thread(
                    name=f'{channel.upper()}_{market}', target=pools[channel], args=(market, subs[0]))
                self._subs_pool.put([market, mkt_threader])

    def _subscription_arbiter(self) -> None:
        """ Gets new subscriptions from _subs_pool queue and starts _sub_market_thread """
        while self._run_event.is_set():
            market_name, market_thread = self._subs_pool.get()
            market_thread.start()
            time.sleep(0.25)
            self._subs_pool.task_done()
        self._subs_pool.join()

    def stream_wizard(self, streamers: Dict[str, Tuple[Optional[float], Tuple[str, ...]]]) -> None:
        """ TODO docstring this mf """
        if not self._run_event.is_set():
            self._run_event.set()
        if self._thread_pooler is None:
            self._thread_pooler = Thread(name='_ARBITER', target=self._subscription_arbiter, daemon=True)
            self._thread_pooler.start()
        market_pool = Thread(name='_MARKET_POOL', target=self._stream_pooler, args=(streamers,))
        safe_writes = Thread(name='_WRITE_WIZARD', target=self._write_worker)
        market_pool.start()
        time.sleep(0.5)
        safe_writes.start()
        try:
            while 1:
                time.sleep(5)
        except KeyboardInterrupt:
            print()
            logging.debug(f'\n>>> KeyboardInterrupt:[ _TERMINATE_THREAD_POOL ]')
            self._run_event.clear()
            market_pool.join()
            safe_writes.join()
            self.disconnect()
        finally:
            print(f'\n>>> Enumerate Threads: ')
            for ti in enumerate_threads():
                print(f'>>> LiveThread: [{ti}]')
            return


if __name__ == '__main__':
    print(f'>>> Running FTX_OrderbooksClient as {__name__}\n')
    socks = ClientSocket()
    # lol = ('BTC/USD', )
    # lol = ('BTC/USD', 'BTC/USDT', 'BTC-PERP', 'BTC/TRYB', 'ETH/USD', 'ETH/USDT', 'ETH/BTC', 'ETH-PERP')
    # socks.stream_wizard({'orderbook': (2, lol), 'trades': (12, lol), 'tickers': (10, lol)})
    lol = ('BTC/USD',)
    socks.stream_wizard({'trades': (3, lol)})


else:
    print(f'>>> Running FTX_OrderbooksClient as {__name__}\n')

#
#
#
#
#
#
# # #
    # def _orderbook_wizard(self, many_markets: Tuple[str, ...]) -> None:
    #     """
    #     Protected method: Breaks many markets into single markets
    #     Iterates over many_market_names(or_one) threading each
    #     """
    #     logging.debug('<<< _POLL_WIZARD.started(protected) >>>')
    #     # self._thread_pool_starter()
    #     for single_market in many_markets:
    #         # self._market_pool(single_market.upper())
    #         pass
    #
    # def _market_pool(self, market: str):
    #     """
    #     Protected method: Manages polling queue
    #     Creates thread tasked with polling XYZ market, FIFO.put for processing
    #     """
    #     logging.debug(f'>>> _START_POOL.QUEUE_GET: [ {market} ]')
    #     threader = Thread(name=f'POLL_{market}', target=self._polling_manager, args=(market,))
    #     threader.setDaemon(True)
    #     self._unsub_pool.put_nowait(threader)
    #     self._subs_pool.put([market, threader])
    #
    # def _orderbook_wizard(self, many_markets: Tuple[str, ...]) -> None:
    #     """
    #     Protected method: Breaks many markets into single markets
    #     Iterates over many_market_names(or_one) threading each
    #     """
    #     logging.debug('<<< _POLL_WIZARD.started(protected) >>>')
    #     self._thread_pool_starter()
    #     for single_market in many_markets:
    #         self._market_pool(single_market.upper())
    #
    # def _serial_killer(self):
    #     """
    #     Protected method: Thread joiner
    #     ATTEMPTS graceful exit. Called on raise ExitTypeInterrupt. . .
    #     """
    #     try:
    #         while True:
    #             kill_thread = self._unsub_pool.get_nowait()
    #             logging.debug(f'>>> Attempting kill_thread.join(): {kill_thread}')
    #             kill_thread.join(timeout=3.0)
    #             time.sleep(0.5)
    #     except Exception as e:
    #         logging.debug(f'>>> raised EmptyException?: {e}')
    #     finally:
    #         return


# class StartClientServer:
#     # _HOST_ID = socket.gethostbyname(socket.gethostname())
#     _HOST_ID = 'localhost'
#     _PORT_NUM = 55555
#
#     def __init__(self, client_server=None):
#         super().__init__()
#         self.client_server = client_server
#         self.client_queue = queue.Queue()
#         self.new_client = None
#
#     def _run_client_server(self):
#         raise NotImplementedError()
#
#     def _start_client_server(self):
#         assert not self.client_server, 'must not already be an idiot'
#         self.client_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.client_server.bind((self._HOST_ID, self._PORT_NUM))
#         self.client_server.listen(1)
#
#     def start_client_server(self):
#         if self.client_server is None:
#             self._start_client_server()
#         assert self.client_server, 'must be an idiot first'
#         self._run_client_server()
#
#
# class RunClientServer(StartClientServer):
#     def __init__(self):
#         super().__init__()
#         # self.wait_cs_socket =
#
#     def _run_client_server(self):
#         pass
#
#     def run_client_server(self):
#         assert self.client_server, 'must be an idiot first'
#         while True:
#             self.client_queue.put(self.client_server.accept())

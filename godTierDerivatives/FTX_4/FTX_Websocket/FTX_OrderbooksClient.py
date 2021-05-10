# from ftx_only_orderbook import FtxWebsocketClient, logging, Thread, Event
# from gevent import socket
# import greenlet
from queue import Queue
from FTX_Orderbooks import *


class ClientSocket(FtxWebsocketClient):
    """
    Create class instance and pass tuple with market names to .heavy_wizard()
    Socket is opened with exchange server, subscription requests sent
    Efficient wait loop for orderbook updates implemented with gevent.Event
    """
    def __init__(self):
        """ All attributes _protected to preserve proper synchronization pattern """
        super().__init__()
        self._subs_pool = Queue()  # check: _polling_manager docstring
        self._write_pool = Queue()  # check: _write_wizard docstring
        self._dis_locker = Lock()  # check: _serial_killer
        self._run_event = Event()  # waits for exit interrupt
        self._thread_pool = None  # subscription arbiter pseudo_thread

    def _serial_killer(self, poll_wizard):
        """
        Protected method: Thread joiner
        ATTEMPTS graceful exit. Called on raise ExitTypeInterrupt. . .
        """
        with self._dis_locker:
            logging.debug('>>> _run_event.clear()')
            self._run_event.clear()
            logging.debug('>>> heavy_wizardry.join()')
            poll_wizard.join()
            logging.debug('>>> self.disconnect()')
            self.disconnect()
            logging.debug('>>> self._write_pool.join()')
            self._write_pool.join()

    def _write_wizard(self):
        """
        Processes queued items for safe-writes to file.txt
        TODO raise NotImplementedError() -> database_handler.inherit
        """
        while True:
            market, update, update_ts, polling = self._write_pool.get()
            valid_name = ''.join(['_' if x in '/' else x for x in market]).upper()
            try:
                with open(file=f'../temp_storage/{valid_name}_{polling}.txt', mode='a+') as filer:
                    filer.writelines(f'UPDATED_TS: {update_ts}\nDATA_SAMPLE: {update}\n')
                self._write_pool.task_done()
            except Exception as e:
                raise logging.debug(f'ExceptionRaised._poll_writer: {e}')

    def _polling_manager(self, market: str):
        """
        Protected method, 'wait_for_ordbk_update' event handler
        Upon update, object queued for safe writes.
        """
        logging.debug('<<< _POLLING_MANAGER.started(protected) >>>')
        while self._run_event.is_set():
            mkt_ordbk, ordbk_ts = self.get_orderbook(market=market), \
                                  self.get_orderbook_timestamp(market=market)
            self._write_pool.put([market, mkt_ordbk, ordbk_ts, 'ordbk'])
            logging.debug(f'>>> Orderbook.recv({market}):[<{ordbk_ts}>]')
            # time.sleep(2)
            self.wait_for_orderbook_update(market=market, timeout=5.0)

    def _market_pool(self, market: str):
        """
        Protected method: Manages polling queue
        Inserts new subscriptions to _subs_pool queue
        """
        logging.debug(f'>>> _START_POOL.QUEUE_GET: [ {market} ]')
        threader = Thread(name=f'POLL_{market}', target=self._polling_manager, args=(market,))
        self._subs_pool.put([market, threader])

    def _sub_pool_arbiter(self):
        """
        Protected method: Subscription pooling queue arbiter
        Gets new subscriptions from _subs_pool queue and starts market_thread
        """
        while self._run_event.is_set():
            market_name, mkt_thread = self._subs_pool.get()
            logging.debug(f'>>> _START_POOL.QUEUE_GET: [ {market_name} ]')
            mkt_thread.start()
            time.sleep(0.5)
            self._subs_pool.task_done()

    def _thread_pool_starter(self):
        """
        Protected method: Initializes subscription pool arbiter -> if None, else pass
        Initializes _pool_arbiter subscription manager
        """
        if self._thread_pool is not None:
            return
        else:
            self._thread_pool = Thread(name='_POOL_ARBITER', target=self._sub_pool_arbiter, daemon=True)
            self._thread_pool.start()

    def _handle_sub(self, market: str) -> None:
        """
        Protected method: Single market name queue handler
        Sets letters uppercase, best practice pass uppercase either way
        """
        self._thread_pool_starter()
        self._market_pool(market.upper())

    def _orderbook_wizard(self, many_markets: Tuple[str, ...]) -> None:
        """
        Protected method: Breaks many markets into single markets
        Iterates over many_market_names(or_one) threading each
        """
        logging.debug('<<< _POLL_WIZARD.started(protected) >>>')
        for single_market in many_markets:
            self._handle_sub(single_market)

    def orderbook_wizard(self, markets: Tuple[str, ...]) -> None:
        """
        Takes: Tuple(market_name, ...) as they're listed on FTX.com
        Implicit formatting on market_name to ensure safe file designator path
        """
        self._run_event.set()
        poll_wizard = Thread(name='_POLL_WIZARD', target=self._orderbook_wizard, args=(markets,))
        write_wizard = Thread(name='_WRITE_WIZARD', target=self._write_wizard, daemon=True)
        kill_wizard = Thread(name='_KILL_WIZARD', target=self._serial_killer, args=(poll_wizard, ))
        poll_wizard.start()
        write_wizard.start()
        try:
            while 1:
                time.sleep(5)
        except KeyboardInterrupt:
            print()
            logging.debug('>>> KeyboardInterrupt:[ _KILL_THREAD_POOL ]')
            kill_wizard.start()
            with self._dis_locker:
                logging.debug('>>> WAITING FOR SERIAL_KILLER')
            raise SystemExit
        finally:
            kill_wizard.join(timeout=2)
            logging.debug('>>> TERMINATED(CLIENT SOCKET & POLL_THREADS)')
            return


if __name__ == '__main__':
    socks = ClientSocket()
    socks.orderbook_wizard(('BTC/USD',))
    # socks.orderbook_wizard((
    #     'BTC/USD', 'BTC/USDT', 'BTC-PERP', 'BTC/TRYB',
    #     'ETH/USD', 'ETH/USDT', 'ETH/BTC', 'ETH-PERP'
    # ))

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

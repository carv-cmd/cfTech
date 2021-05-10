# from ftx_only_orderbook import FtxWebsocketClient, logging, Thread, Event
# from gevent import socket
# import greenlet
import time
import queue
from FTX_Orderbooks import *


class ClientSocket(FtxWebsocketClient):
    def __init__(self):
        super().__init__()
        self._start_pool = queue.Queue()
        self._write_pool = queue.Queue()
        self._run_event = Event()
        self._write_event = Event()
        self._dis_locker = Lock()
        self._thread_pool = None

    def _poll_writer(self):
        while True:
            market, ts, update = self._write_pool.get()
            valid_name = ''.join(['_' if x in '/' else x for x in market]).upper()
            try:
                with open(file=f'../temp_storage/{valid_name}.txt', mode='a+') as filer:
                    filer.writelines(f'UPDATED_TS: {ts}\nDATA_SAMPLE: {update}\n')
                self._write_pool.task_done()
            except Exception as e:
                raise logging.debug(f'ExceptionRaised._poll_writer: {e}')

    def _polling_manager(self, mkt: str, test_delay: float = 2):
        logging.debug('<<< _POLLING_MANAGER.started(protected) >>>')
        while self._run_event.is_set():
            ts, obs = self.get_orderbook_timestamp(market=mkt), self.get_orderbook(market=mkt)
            self._write_pool.put([mkt, ts, obs])
            logging.debug(f'>>> Orderbook.recv({mkt}):[<{ts}>]')
            # time.sleep(test_delay)
            self.wait_for_orderbook_update(market=mkt, timeout=5.0)

    def _pool_polling(self, market: str):
        logging.debug(f'>>> _START_POOL.QUEUE_GET: [ {market} ]')
        threader = Thread(name=f'POLL_{market}', target=self._polling_manager, args=(market,))
        self._start_pool.put([market, threader])

    def _pool_arbiter(self):
        while self._run_event.is_set():
            market, starting = self._start_pool.get()
            logging.debug(f'>>> _START_POOL.QUEUE_GET: [ {market} ]')
            starting.start()
            time.sleep(0.5)

    def _live_thread_pool(self) -> None:
        if self._thread_pool is not None:
            return
        else:
            self._thread_pool = Thread(name='_POOL_ARBITER', target=self._pool_arbiter, daemon=True)
            self._thread_pool.start()

    def _serial_killer(self, heavy_wizardry) -> None:
        with self._dis_locker:
            logging.debug('>>> _run_event.clear()')
            self._run_event.clear()
            logging.debug('>>> heavy_wizardry.join()')
            heavy_wizardry.join()
            logging.debug('>>> self.disconnect()')
            self.disconnect()
            logging.debug('>>> self._write_pool.join()')
            self._write_pool.join()

    def _poll_single(self, market: str) -> None:
        self._live_thread_pool()
        self._pool_polling(market)

    def _poll_wizard(self, many_markets: Tuple[str, ...]) -> None:
        logging.debug('<<< _POLL_WIZARD.started(protected) >>>')
        for single_market in many_markets:
            self._poll_single(single_market)

    def poll_wizard(self, markets: Tuple[str, ...]):
        self._run_event.set()
        heavy_wizard = Thread(name='_HEAVY_WIZARD', target=self._poll_wizard, args=(markets,))
        write_wizard = Thread(name='_WRITE_WIZARD', target=self._poll_writer, daemon=True)
        kill_wizard = Thread(name='_KILL_WIZARD', target=self._serial_killer, args=(heavy_wizard, ))
        heavy_wizard.start()
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
            logging.debug(f'>>> write_wizard.isAlive({write_wizard.is_alive()})')
            logging.debug('>>> TERMINATED CLIENT SOCKET & POLLING THREADS')
            return


if __name__ == '__main__':
    socks = ClientSocket()
    # socks.poll_wizard(('BTC/USD', ))
    socks.poll_wizard(('BTC/USD', 'BTC/USDT', 'BTC-PERP'))


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
















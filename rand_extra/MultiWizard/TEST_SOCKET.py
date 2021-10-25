import time
import json
import random
import logging
import socket
from datetime import datetime
from threading import Thread, Condition, Lock, Event
from typing import Optional, Any

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s')


class PseudoUpdates:
    def __init__(self):
        self._bids = None
        self._asks = None
        self.remote_client = None
        self.client_lock = Condition()

    def _send_update(self, remote):
        raise NotImplementedError()

    def _pseudo_updates(self,
                        runs: Event,
                        write_event: Event,
                        read_lock: Condition,
                        delay: float) -> None:
        while runs.is_set():
            time.sleep(random.random() * delay)
            self._bids, self._asks = random.randint(25, 30), random.randint(23, 28)
            with read_lock:
                write_event.set()
                read_lock.wait()

    def _on_update(self,
                   rem: socket.socket,
                   runs: Event,
                   write_event: Event,
                   read_lock: Condition) -> None:
        try:
            while runs.is_set():
                write_event.wait()
                with read_lock:
                    write_event.clear()
                    self._send_update(remote=rem)
                    read_lock.notifyAll()
        except Exception as e:
            logging.debug(f'<< _REMOTE_CLIENT_DISCONNECTED:\n{e} >>')

    def update_factory(self, delay: Optional[float]) -> None:
        run_event = Event()
        run_event.set()
        write_event = Event()
        read_lock = Condition()
        writer = Thread(name='_WRITER',
                        target=self._pseudo_updates,
                        args=(run_event, write_event, read_lock, delay))
        reader = Thread(name='_READER',
                        target=self._on_update,
                        args=(self.remote_client, run_event, write_event, read_lock))
        writer.start()
        reader.start()


class ServerSock(PseudoUpdates):
    _PORT = 55555
    _HOST_ID = socket.gethostbyname(socket.gethostname())

    def __init__(self):
        super().__init__()
        self.serve_sock = None

    def _reset(self) -> Any:
        if self._asks and self._bids:
            return
        else:
            del self._bids, self._asks

    def _send_update(self, remote: socket.socket) -> None:
        locker = Lock()
        locker.acquire(blocking=True, timeout=0.25)
        serve = json.dumps({'updates': {'bids': self._bids, 'asks': self._asks}})
        logging.debug(f"SEND-> {serve}")
        remote.send(serve.encode('utf-8'))
        self._reset()
        locker.release()

    def _terminate_socket(self) -> None:
        self.serve_sock.close()

    def _client_handler(self, live_socket, delay: Optional[float]) -> None:
        if not live_socket.is_set():
            self._terminate_socket()
        else:
            self.update_factory(delay=delay)

    def _inet_tcp_socket(self):
        logging.debug('* _INET_TCP_SOCKET(protected).started. . .')
        assert not self.serve_sock, logging.debug('dont be an idiot')
        self.serve_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serve_sock.bind((self._HOST_ID, self._PORT))
        self.serve_sock.listen(5)

    def inet_tcp_sock(self, live_socket: Event, delay: Optional[float]) -> None:
        logging.debug('* _INET_TCP_SOCK.starting(_create_socket). . .')
        if not self.serve_sock:
            self._inet_tcp_socket()
        assert self.serve_sock, logging.debug('socket must be live to listen')

        while live_socket.is_set():
            logging.debug('>>>> while True: accepting_persistent_connections. . .\n')
            try:
                self.remote_client, address = self.serve_sock.accept()
                logging.debug(f'>>> Connected: [address: {address}]\n')
                connected = Thread(name=address, target=self._client_handler,
                                   args=(live_socket, delay))
                connected.start()
            except Exception as e:
                raise e

    def streamer_socket(self, delay: Optional[float] = 0.25) -> None:
        live_socket = Event()
        logging.debug('* _STREAMER_SOCKET.starting(host)')
        live_socket.set()
        streams = Thread(name='_HOST_SOCKET', target=self.inet_tcp_sock,
                         args=(live_socket, delay))
        streams.start()
        try:
            while 1:
                time.sleep(5)
        except KeyboardInterrupt:
            live_socket.clear()
            streams.join()
        finally:
            print("\n>>> _TERMINATED_WEBSOCKET_SERVER")


if __name__ == '__main__':
    print(f'\n>>> Initialized SERVER_SOCKET: '
          f"[ {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} ]\n")
    socks = ServerSock()
    socks.streamer_socket(delay=1)


###################################################
###################################################
###################################################
# class ServingSocket:
#     _PORT = 55555
#     _SOCKET = socket
#
#     def __init__(self):
#         self._run_event = Event()
#         self.sock_server = None
#         self._bids = None
#         self._asks = None
#
#     def _terminate_socket(self):
#         assert self.sock_server, 'how can you close something that is closed dipshit'
#         self.sock_server.close()
#
#     def _reset_msg(self):
#         if not self._bids and self._asks:
#             return
#         else:
#             del self._bids
#             del self._asks
#
#     def _send_update(self, CLIENT: socket.socket):
#         dump = json.dumps({'updates': {'bids': self._bids, 'asks': self._asks}})
#         logs.debug(f'* SENT -> {dump}')
#         CLIENT.send(dump.encode('utf-8'))
#         self._reset_msg()
#
#     def _pseudo_update(self, write_lock, read_lock, delay: float = 1.0):
#         logs.debug('> _SET_update.initiated. . .')
#         while True:
#             with write_lock:
#                 time.sleep(random.random() * delay)
#                 self._bids, self._asks = random.randint(750, 1000), random.randint(750, 1000)
#                 write_lock.notifyAll()
#             with read_lock:
#                 read_lock.wait(timeout=5)
#
#     def _get_update(self, write_lock, read_lock, CLIENT):
#         logs.debug('> _GET_update.initiated. . .\n')
#         while True:
#             with write_lock:
#                 write_lock.wait(timeout=5)
#             with read_lock:
#                 try:
#                     self._send_update(CLIENT)
#                     read_lock.notifyAll()
#                 except ConnectionAbortedError:
#                     self._terminate_socket()
#
#     def _client_handler(self, CLIENT: socket.socket):
#         write_lock = Condition()
#         read_lock = Condition()
#         make = Thread(name='_SETTER_UPDATE', target=self._pseudo_update,
#                       args=(write_lock, read_lock))
#         get = Thread(name='_GET_UPDATE', target=self._get_update,
#                      args=(write_lock, read_lock, CLIENT))
#         make.start()
#         time.sleep(1)
#         get.start()
#
#     def _create_inet_tcp(self):
#         logs.debug('* _CREATE_INET_TCP_SOCKET.started. . .')
#         assert not self.sock_server, logs.debug('INET_TCP socket already active')
#         self.sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock_server.bind((socket.gethostbyname(socket.gethostname()), self._PORT))
#         self.sock_server.listen()
#
#     def inet_tcp_sock(self):
#         logs.debug('* _INET_TCP_SOCK.starting(_create_socket). . .')
#         if not self.sock_server:
#             self._create_inet_tcp()
#         assert self.sock_server, logs.debug('socket must be live to listen')
#         while self._run_event.is_set():
#             logs.debug('>>>> while True: accepting_persistent_connections. . .\n')
#             try:
#                 remote, address = self.sock_server.accept()
#                 logs.debug(f'>>> Connected to: [address: {address}]')
#                 connected = Thread(name=address, target=self._client_handler, args=(remote, ))
#                 connected.start()
#             except Exception as e:
#                 raise e
#         self._terminate_socket()
#
#     def streamer_socket(self):
#         logs.debug('* _STREAMER_SOCKET.starting(host) <<<')
#         self._run_event.set()
#         streams = Thread(name='_HOST_SOCKET', target=self.inet_tcp_sock)
#         streams.start()
#         try:
#             while 1:
#                 time.sleep(5)
#         except KeyboardInterrupt:
#             self._run_event.clear()
#             streams.join()
#         finally:
#             print("\n>>> _TERMINATED_WEBSOCKET_SERVER")
#
#
# if __name__ == '__main__':
#     print('\n>>> INITIALIZING HOST SERVER w/ RAND UPDATES. . .\n')
#     socks = ServingSocket()
#     socks.streamer_socket()


    # def _send_update(self, remote_client: socket.socket):
    #     remote_client.send(json.dumps(
    #         {'updates': {'bids': self._bids, 'asks': self._asks}}).encode('utf-8'))
    #
    # def _set_update(self, _write_locks, _read_locks, delay: float = 2.5):
    #     logs.debug('> _SET_update.initiated. . .')
    #     while True:
    #         with _write_locks:
    #             logs.debug('>> _SET_UPDATE.blocking(I/O). . .')
    #             time.sleep(random.random() * delay)
    #             self._bids, self._asks = random.randint(750, 1000), random.randint(750, 1000)
    #             _write_locks.notifyAll()
    #         with _read_locks:
    #             logs.debug('>>> _UPDATED.wait(read_lock)')
    #             _read_locks.wait(timeout=2)
    #
    # def _get_update(self, _write_locks, _read_locks, remote_client: socket.socket):
    #     logs.debug('> _GET_update.initiated. . .\n')
    #     while True:
    #         with _write_locks:
    #             logs.debug('>> _GET_UPDATE.wait(write_lock). . .')
    #             _write_locks.wait(timeout=2)
    #         with _read_locks:
    #             self._send_update(remote_client)
    #             self._reset_msg()
    #             _read_locks.notifyAll()

    # def _client_handler(self, CLIENT: socket.socket):
    #     logs.debug(f'* _CLIENT_HANDLER.started. . .')
    #     _read = Condition()
    #     _write = Condition()
    #     writes = Thread(name='_SETTER_UPDATE', target=self._set_update, args=(_read, _write))
    #     reads = Thread(name='_GET_UPDATE', target=self._get_update, args=(_read, _write, CLIENT,))
    #     writes.start()
    #     time.sleep(1)
    #     reads.start()

    # def _client_handler(self, client_obj: socket.socket):
    #     logs.debug(f'* _CLIENT_HANDLER.started. . .')
    #     _locker = Condition()
    #     _update_events = Event()
    #     writes = Thread(name='_DATA_WRITER',
    #                     target=self._start_pseudo_stream,
    #                     args=(_update_events,))
    #     reads = Thread(name='_DATA_READER',
    #                    target=self._get_pseudo_update,
    #                    args=(client_obj, _update_events))
    #     writes.start()
    #     time.sleep(2)
    #     reads.start()
# def shared(new: Optional[str] = None):
#     global ccv
#     with ccv:
#         print(f"Shared_Accessed@:[ <{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}> ]")
#         time.sleep(random.random() * 2)
#         try:
#             with open('TEST_SAVE.txt.txt', mode='a+') as filer:
#                 if not new:
#                     return list(filer.read())
#                 else:
#                     filer.write(f'{new}\n')
#         except Exception as e:
#             raise e
#         finally:
#             print('\n>>> notify_all()')
#             ccv.notify_all()
#
#
# def _notify_update():
#
#
#
# def _read_updates():
#     print(f'\n>>> Shared: {shared()}')
#     ccv.notify_all()
#
#
# def _write_updates(run_event, reader, sharing, n: float = 2.0):
#     global ccv
#     while run_event.is_set():
#         sharing.run()
#         # print(f'\n>>> _write_1.ccv.locked = {locky.locked()}')
#         # shared(json.dumps({'update': [
#         #     ('bids', [random.randint(15, 25) for b in range(2)]),
#         #     ('asks', [random.randint(12, 27) for a in range(2)])]
#         # }))
#         with ccv:
#             # print(f'\n>>> _write_2.ccv.locked = {locky.locked()}')
#             ccv.wait_for(shared)
#             reader.run()
#
#
# def testing():
#     run_event = Event()
#     run_event.set()
#
#     shared_thread = Thread(
#         target=shared,
#         args=(
#             json.dumps({'update': [
#                 ('bids', [random.randint(15, 25) for b in range(2)]),
#                 ('asks', [random.randint(12, 27) for a in range(2)])]
#             })))
#     shared_thread.start()
#
#     read_thread = Thread(target=_read_updates)
#     read_thread.setDaemon(True)
#     write_thread = Thread(target=_write_updates,
#                           args=(run_event, read_thread, shared_thread))
#
#     time.sleep(1.5)
#     write_thread.start()
#     time.sleep(1.5)
#     read_thread.start()
#
#     try:
#         while 1:
#             time.sleep(5)
#     except KeyboardInterrupt:
#         run_event.clear()
#         write_thread.join()
#         time.sleep(0.5)
#     finally:
#         print('>>> fuck me; it worked. . .')
#
#     return
#
#


# Gather data for a period of 30 sec from ftx servers
# Create while loop with random delay between [ 0.1 - 1.0 ]
# Server: waits -> readline_from_dump -> notifies_active_listeners
#   socket = {
#     'socket': [*INTERNET:(AF_INET), UNIX:()],
#     'connection': [*TCP:(SOCK_STREAM), UDP:(SOCK_DEGRAM)],
#     'ip(host|conn)': [socket.gethostbyname(socket.gethostname())],
#     'port': [<any(non-standard_TCP_enabled)>]
#   }

######################################################
######################################################
######################################################
#
# import json
# import socket
# from threading import Thread, Event, Lock, Condition
# from datetime import datetime
# import time
# import random
# # import gevent
# # import greenlet
#
# _SHARED_RESOURCE = []
# s_locks = Lock()
# ccv = Condition(lock=s_locks)
#
#
# def _gen_updates(run_event: Event, n: int = 5):
#     global _SHARED_RESOURCE, ccv
#     while run_event.is_set():
#         with ccv:
#             time.sleep(random.random() * (n / 2))
#             _SHARED_RESOURCE.append(
#                 json.dumps(
#                     {'update': [
#                         ('bids', [random.random() * n for b in range(2)]),
#                         ('asks', [random.random() * n for a in range(2)])
#                     ]}).encode('utf-8'))
#             ccv.notify()
#
#
# def _on_update(remote):
#     global _SHARED_RESOURCE, ccv
#     remote.send(_SHARED_RESOURCE[-1])
#
#
# def _sock_streams(run_event: Event, remote: socket.socket, address: tuple, delay: float):
#     global ccv
#     while run_event.is_set():
#         send_thread = Thread(target=_on_update, args=(remote,))
#         send_thread.setDaemon(True)
#         send_thread.start()
#         print(f'\n>>> Maintain Persistent PseudoRandom Updates to: [ {address} ]')
#         time.sleep(random.random() * delay)
#         with ccv:
#             ccv.wait_for(_gen_updates, timeout=5)
#             send_thread.run()
#     remote.send(_on_close())
#     return
#
#
# def _on_close():
#     return json.dumps({'op': 'terminate'}).encode('utf-8')
#
#
# def _server_socket(run_event: Event, delay: float):
#     serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     serv_sock.bind((socket.gethostbyname(socket.gethostname()), 55555))
#     serv_sock.listen()
#     while run_event.is_set():
#         try:
#             serv_client, address = serv_sock.accept()
#             print(f'>>> Connected to: [address: {address}]')
#             client_thread = Thread(
#                 target=_sock_streams,
#                 args=(run_event, serv_client, address, delay))
#             client_thread.start()
#         except Exception as e:
#             raise e
#
#
# def server(delay: float = 2.0):
#     run_event = Event()
#     run_event.set()
#     updated = Thread(target=_gen_updates, args=(run_event,))
#     thread_server = Thread(target=_server_socket, args=(run_event, delay))
#     updated.start()
#     thread_server.start()
#     try:
#         while 1:
#             time.sleep(5)
#     except KeyboardInterrupt:
#         run_event.clear()
#         thread_server.join()
#         raise SystemExit
#     finally:
#         print('\n>>> Server Socket terminated successfully. . .')
#
#
# if __name__ == '__main__':
#     print(f'\n>>> Initialized TEST_SOCKET.py at: '
#           f"[ <{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}> ]\n")
#     server()

######################################################
######################################################
######################################################

# from threading import Thread, Event, Lock, Condition
# import socket

# locks = Lock()
# cond = Condition(lock=locks)
# _SHARED_RES = []
# _FLAG = locks.locked
# def _pseudo_update(run_event: Event):
#     global cond, _SHARED_RES
#     while run_event.is_set():
#         with cond:
#             try:
#                 new_update = json.dumps(
#                     {'orders': [
#                         ('bid', random.randint(25, 35)),
#                         ('ask', random.randint(24, 36))]})
#                 time.sleep(random.random() * 2)
#                 _SHARED_RES.append(new_update)
#             except Exception as e:
#                 print(f'Exception(e): {e}')
#             finally:
#                 # _update_available.notify()
#                 pass
#     return
#
#
# def _update_available(run_event: Event):
#     thread_updates = Thread(target=_pseudo_update, args=(run_event, ))
#     thread_updates.setDaemon(True)
#     thread_updates.start()
#     while run_event.is_set():
#         with cond:
#             cond.wait_for(_pseudo_update)
#             print(_SHARED_RES)
#             cond.release()
#
#
# def server_sock():
#     run_event = Event()
#     run_event.set()
#     threaded_updates = Thread(target=_update_available, args=(run_event, ))
#     threaded_updates.run()
#     try:
#         while 1:
#             time.sleep(5)
#     except KeyboardInterrupt():
#         run_event.clear()
#         threaded_updates.join()
#         raise SystemExit
#     finally:
#         return
#
#
# def magic_update():
#     global cond
#     while True:
#         with cond:
#             _SHARED_RES.append(random.random())
#             time.sleep(random.random() * 2)
#             cond.notify_all()
#
#
# def updated():
#     print(f'>>> _SHARED_RES: [{_SHARED_RES}]:[{_SHARED_RES[:-1]}]')
#
#
# def new_cond():
#     global cond, _FLAG
#     magic = Thread(target=updated)
#     magic.start()
#     return magic
#
#
# def poll_cond():
#     global cond, _FLAG
#     ups = Thread(target=magic_update)
#     ups.start()
#     while True:
#         with cond:
#             cond.wait_for(_FLAG, timeout=4.0)
#             ups.run()
#             new_cond().run()

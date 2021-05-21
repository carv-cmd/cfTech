import time
import json
import random
import logging
import socket
from datetime import datetime
from threading import Thread, Condition, Event

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s')
# class SocketHandler:
#     def __init__(self,
#                  on_connect=None, on_disconnect=None, on_reset=None,
#                  on_update=None, on_msg=None):
#         self._on_connect = on_connect
#         self._on_disconnect = on_disconnect
#         self._on_reset = on_reset
#         self._on_update = on_update
#         self._on_msg =
#         self.update_lock = Event()
#
#     def _on_reset(self):
#         raise NotImplementedError()
#
#     def _on_update(self, ws, notify):
#         raise NotImplementedError()
#
#     def _on_msg(self, sock, msg):
#         raise NotImplementedError()
#
#     def _on_disconnect(self, sock):
#         raise NotImplementedError()


class ServerSocket(object):
    _PORT = 55555
    _HOST_ID = socket.gethostbyname(socket.gethostname())

    def __init__(self):
        self.serve_sock = None
        self.live_socket = Event()
        self.bids = None
        self.asks = None
        self.msg = None

    def _on_reset(self):
        raise NotImplementedError()

    def _send_update(self, sock, update):
        raise NotImplementedError()

    def _on_update(self, ws, notify):
        raise NotImplementedError()

    def _on_msg(self, sock, msg):
        raise NotImplementedError()

    def _on_disconnect(self, sock):
        raise NotImplementedError()

    def _client_handler(self, remote_client):
        raise NotImplementedError()

    def _run_forever(self):
        self.live_socket.set()
        while self.live_socket.is_set():
            try:
                logging.debug('* ACCEPTING(max=5).persistent_conn')
                (remote_client, address) = self.serve_sock.listen()
                connected_client = Thread(name=address,
                                          target=self._client_handler,
                                          args=(remote_client, ))
                connected_client.start()
            except Exception as e:
                raise Exception(f'Unexpected error in socket.run({e})')

    def _inet_tcp_socket(self):
        logging.debug('* _INET_TCP_SOCKET(protected_member).started')
        assert not self.serve_sock, logging.debug('dont be an idiot')
        self.serve_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serve_sock.bind((self._HOST_ID, self._PORT))
        self.serve_sock.listen(5)

    def inet_tcp(self):
        logging.debug('* _INET_TCP_SOCK.starting(_create_socket). . .')
        if not self.serve_sock:
            self._inet_tcp_socket()
            assert self.serve_sock, logging.debug('again, dont be idiot')
            self._run_forever()


class ClientHandler(ServerSocket):
    def __init__(self):
        super().__init__()


class ClientSocket(ServerSocket):
    def __init__(self):
        super().__init__()

    def _on_reset(self):  # reset
        if not self.bids and self.asks:
            return
        else:
            del self.bids, self.asks

    def _on_disconnect(self, sock):  # gracefully disconnect
        sock.close()

    def _on_msg(self, sock, msg):  # received from remote
        sock.send(msg)
        pass

    def _on_update(self, ws, notify):  # notify sender
        pass

    def _send_update(self, sock, update):  # sender
        pass

    def _client_handler(self, remote_client):  # incoming clients
        pass


if __name__ == '__main__':
    pass

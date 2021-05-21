import socket
import time
import logging as logs
from datetime import datetime
from threading import Thread, Event, Timer

logs.basicConfig(level=logs.DEBUG,
                 format='(%(threadName)-9s) %(message)s')

LOCAL_HOST = socket.gethostbyname(socket.gethostname())
SAFE_PORT = 55555


def _client_socket(run_event: Event):
    _C_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _C_SOCK.connect((LOCAL_HOST, SAFE_PORT))
    while run_event.is_set():
        update = _C_SOCK.recv(1024)
        logs.debug(f": RECV-> {update.decode('utf-8')}")
    _C_SOCK.close()


def client():
    def terminate_client():
        run_event.clear()
        thread_client.join()
    run_event = Event()
    run_event.set()
    thread_client = Thread(name='_LOCAL_CLIENT',
                           target=_client_socket,
                           args=(run_event, ))
    thread_client.start()
    tits = Timer(120, terminate_client)
    tits.start()
    logs.debug('\n>>> Client Socket Opened. . .')
    try:
        while 1:
            time.sleep(5)
    except KeyboardInterrupt:
        terminate_client()
    finally:
        logs.debug('\n>>> Client Socket connection closed. . .')


if __name__ == '__main__':
    print(f'\n>>> Initialized SERVER_SOCKET: '
          f"[ {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} ]\n")
    client()
    client()

from tkinter import *
from tkinter import ttk
import time
import random
from collections import defaultdict
from threading import Thread, Lock, Event, Condition
from typing import *
# from ..FTX_4.FTX_Websocket.FTX_ws_WorkerClass import Thread, Event, Lock  # StreamWizard


run_event = Event()
main_lock = Lock()
cond_lock = Condition(lock=main_lock)

root = Tk()
root.title('LIVE STREAMING: DUMBFUCK.COM')
delay = 3
market = 'BTC/ETH/DOGE'
G_Dicks = defaultdict()


def _server_thread():
    global cond_lock, run_event
    while run_event.is_set():
        try:
            with cond_lock:
                xyz = random.random()
                print(f'\nWRITE.wait({xyz})')
                G_Dicks[f'SIM_POLL({xyz})'] = [
                    ('bid', xyz * delay),
                    ('ask', (xyz * xyz) / delay)
                ]
                time.sleep(xyz * delay)
        except Exception as e:
            print(f'\n>>> ExceptionRaised({e})')
            raise
        finally:
            cond_lock.notify()


def _client_thread():
    global cond_lock, run_event
    with cond_lock:
        cond_lock.wait_for(_server_thread(), timeout=10)
        print(F'READ(G_List.pop()) = {G_Dicks}')


def dumbass_dot_com(server, client):
    global run_event
    run_event.set()

    server.run()
    time.sleep(0.5)
    client.run()

    try:
        while 1:
            time.sleep(5)
    except KeyboardInterrupt:
        run_event.clear()
        # _server.join()
        raise SystemExit
    finally:
        return


def dot_com():
    _server = Thread(target=_server_thread)
    _client = Thread(target=_client_thread)
    _client.setDaemon(True)

    _server.start()
    _client.start()
    dumbass_dot_com(_server, _client)

    print('>>> SOCKET_CLOSED')


def win_streams(subs: Optional[Tuple[str, Tuple[str, float]]] = None):
    global root

    mf = ttk.Frame(root, padding='3 3 12 12')
    mf.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    update = StringVar()


if __name__ == '__main__':
    print('>>> FTX_main.main')



















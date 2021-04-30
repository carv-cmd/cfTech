import json
import time
from datetime import datetime
from threading import Thread, Event, BoundedSemaphore

from FTX_ws_Client import FtxWebsocketClient

ws_client = FtxWebsocketClient()
timestamp_format = '%Y-%m-%d %H:%M:%S.%f'
sema = BoundedSemaphore(value=1)


def poll_writer(polling_channel: str, ts_daters: list):
    global sema
    sema.acquire()
    try:
        print(f'\n* I/O_Status: <<ATTEMPTING({polling_channel}) WriteOps>>')
        with open(f'../temp_storage/{polling_channel}.txt', mode='a') as file_obj:
            file_obj.write(f'UPDATING_{polling_channel} @: {ts_daters[0]}\n')
            file_obj.write(f"{json.dumps(ts_daters[1])}\n")
            sema.release()
            print(f'\n* I/O_Status: <<SUCCESSFUL({polling_channel}) WriteOps>>')
    except OSError:
        print(f'\n* I/O_Status: <<FAILED({polling_channel}) = [ OSError ]>>')
        raise
    return


def poll_orders(delay, run_event):
    while run_event.is_set():
        time.sleep(delay + 30)
        orders = Thread(
            target=poll_writer,
            args=(f'ORDERS_ALL',
                  [datetime.now().strftime(timestamp_format),
                   ws_client.get_orders()],))
        orders.setDaemon(True)
        orders.start()


def poll_fills(delay, run_event):
    while run_event.is_set():
        time.sleep(delay + 30)
        fills = Thread(
            target=poll_writer,
            args=(f'FILLS_ALL',
                  [datetime.now().strftime(timestamp_format),
                   ws_client.get_fills()],))
        fills.setDaemon(True)
        fills.start()


def poll_trades(mkt, delay, run_event):
    while run_event.is_set():
        time.sleep(delay + 30)
        trades = Thread(
            target=poll_writer,
            args=(f'TRADES_{mkt}',
                  [datetime.now().strftime(timestamp_format),
                   ws_client.get_trades(market=mkt)],))
        trades.setDaemon(True)
        trades.start()


def poll_tickers(mkt, delay, run_event):
    while run_event.is_set():
        time.sleep(delay)
        tickers = Thread(
            target=poll_writer,
            args=(f'TICKERS_{mkt}',
                  [datetime.now().strftime(timestamp_format),
                   ws_client.get_ticker(market=mkt)],))
        tickers.setDaemon(True)
        tickers.start()


def poll_orderbook(mkt, delay, run_event):
    while run_event.is_set():
        time.sleep(delay)
        orders = Thread(
            target=poll_writer,
            args=(f'ORDERBOOK_{mkt}',
                  [ws_client.get_orderbook_timestamp(market=mkt),
                   ws_client.get_orderbook(market=mkt)],))
        orders.setDaemon(True)
        orders.start()


def stream_wizard(market: str,
                  delay: float = 0.5,
                  stream_orderbook: bool = False,
                  stream_tickers: bool = False,
                  stream_trades: bool = False,
                  stream_fills: bool = False,
                  stream_orders: bool = False):

    run_event = Event()
    run_event.set()

    pt_orderbook = Thread(target=poll_orderbook, args=(market, delay, run_event))
    pt_tickers = Thread(target=poll_tickers, args=(market, delay, run_event))
    pt_trades = Thread(target=poll_trades, args=(market, delay, run_event))
    pt_fills = Thread(target=poll_fills, args=(delay, run_event))
    pt_orders = Thread(target=poll_orders, args=(delay, ))

    zipper = list(zip(
        [stream_orderbook, stream_trades, stream_tickers, stream_fills, stream_orders],
        [pt_orderbook, pt_trades, pt_tickers, pt_fills, pt_orders]
    ))

    for starting in list(zipper):
        if not starting[0]:
            pass
        else:
            starting[1].start()
            time.sleep(0.5)

    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f'\n> Attempting -> TerminateAllActiveThreads[ MAX_WAIT=({delay})sec ]')
        run_event.clear()
        for stop in list(zipper):
            if stop[0]:
                stop[1].join()
                print(f'\n> TerminatingThread( <name[{stop[1].name}]> : <id[{stop[1].ident}]> )'
                      f'\n>> Thread({stop[1].name}).isAlive = {stop[1].is_alive()}')
        else:
            print('>>> execute(TerminateAllActiveThreads) = SuccessfulFailure')
            ws_client.disconnect()


if __name__ == '__main__':
    print(f'>>> Running FTX_ws_Worker as {__name__}')

    stream_wizard(
        market='BTC-PERP',
        delay=1,
        stream_orderbook=True,
        stream_tickers=True,
        stream_trades=False,
        stream_orders=False,
        stream_fills=False,
    )

else:
    print(f'>>> Running FTX_ws_Worker as {__name__}')

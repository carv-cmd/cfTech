import json
import time
from datetime import datetime
from threading import Thread, Event, Lock
from threading import enumerate as enumerate_threads

from FTX_ws_Client import FtxWebsocketClient, Optional

ws_client = FtxWebsocketClient()
timestamp_format = '%Y-%m-%d %H:%M:%S.%f'
locker = Lock()


def poll_writer(polling_channel: str, ts_daters: list):
    """ TODO Generate docstring for poll_writer function """
    global locker
    locker.acquire()
    print(f'\n* I/O_LOCK({locker.locked()}): <<ATTEMPT({polling_channel}).write()>>')

    if not ts_daters[1]:
        print('>>>> SKIPPED EMPTY POLL <<<<')
        locker.release()
        return None

    try:
        with open(f'../temp_storage/{polling_channel}.txt', mode='a') as file_obj:
            file_obj.write(f"{json.dumps({f'REFRESH_{polling_channel}': ts_daters[0]})}\n")
            file_obj.write(f"{json.dumps({f'UPDATED': ts_daters[1]})}\n")
    except OSError:
        print(f'\n*** <<WRITE_FAILED:[ {polling_channel} ]>>')
        raise
    finally:
        locker.release()
        print(f'\n** I/O_LOCK({locker.locked()}): <<SUCCESS({polling_channel}).write()>>')
        return


def valid_file_names(markets):
    return ''.join(['_' if x in '/' else x for x in markets])


def poll_fills(run_event: Event, delay: float):
    """ Reference "poll_orderbook" docstring for parameters """
    while run_event.is_set():
        time.sleep(delay)
        fills = Thread(
            target=poll_writer,
            args=(f'FILLS_ALL',
                  [datetime.now().strftime(timestamp_format),
                   ws_client.get_fills()],))
        fills.start()


def poll_orders(run_event: Event, delay: float):
    """ Reference "poll_orderbook" docstring for parameters """
    while run_event.is_set():
        time.sleep(delay)
        orders = Thread(
            target=poll_writer,
            args=(f'ORDERS_ALL',
                  [datetime.now().strftime(timestamp_format),
                   ws_client.get_orders()],))
        orders.start()


def poll_trades(run_event: Event, mkt: str, delay: float):
    """ Reference "poll_orderbook" docstring for parameters """
    mkt_file = valid_file_names(mkt)
    while run_event.is_set():
        time.sleep(delay)
        trades = Thread(
            target=poll_writer,
            args=(f'TRADES_{mkt_file}',
                  [datetime.now().strftime(timestamp_format),
                   ws_client.get_trades(market=mkt)],))
        trades.start()


def poll_tickers(run_event: Event, mkt: str, delay: float = 2.0):
    """ Reference "poll_orderbook" docstring for parameters """
    mkt_file = valid_file_names(mkt)
    while run_event.is_set():
        time.sleep(delay)
        tickers = Thread(
            target=poll_writer,
            args=(f'TICKERS_{mkt_file}',
                  [ws_client.get_ticker_timestamp(market=mkt),
                   ws_client.get_ticker(market=mkt)],))
        tickers.start()


def poll_orderbook(run_event: Event, mkt: str, delay: float = 0.25):
    """
    Continuously polls <some_ftx_market> _orderbook w/ default rate = 0.25sec
    :param mkt: Name of the market to poll. -> ex: mkt='BTC-PERP' (str)
    :param delay: Delay between polling FTX servers. -> default: delay='0.25' (float)
    :param run_event: Synchronization object from main thread. <<<Ignore>>>
    :return: Client-Side-Timestamp Response_Obj -> push to respective save location
    """
    mkt_file = valid_file_names(mkt)
    while run_event.is_set():
        time.sleep(delay)
        orderbooks = Thread(
            target=poll_writer,
            args=(f'ORDERBOOK_{mkt_file}',
                  [ws_client.get_orderbook_timestamp(market=mkt),
                   ws_client.get_orderbook(market=mkt)],))
        orderbooks.start()


def stream_wizard(market: str, *,
                  stream_orderbook: Optional[bool] = False,
                  ord_bk_delay: float = 0.25,
                  stream_tickers: Optional[bool] = False,
                  tick_delay: float = 0.1,
                  stream_trades: Optional[bool] = False,
                  trades_delay: float = 10,
                  stream_fills: Optional[bool] = False,
                  orders_delay: float = 5,
                  stream_orders: Optional[bool] = False,
                  fills_delay: float = 5):
    """
    Call stream_wizard w/ stream_x(True) to establish websocket stream connection
    :param market: FTX market to stream from; ex( "BTC-PERP" or "BTC/USDT")
    :param stream_orderbook: Stream market orderbook data.
    :param stream_tickers: Stream market ticker data.
    :param stream_trades: Stream market trades data.
    :param stream_fills: Stream user account fills data.
    :param stream_orders: Stream user account orders data.
    :return: "Concurrently" writes files to disk or database
    """

    # Initialize 'event loop' for KeyboardInterrupt listener
    run_event = Event()
    run_event.set()

    # Event_loop_obj, market name, and 'global' delay are bound to target on assignment
    pt_orderbook = Thread(target=poll_orderbook, args=(run_event, market, ord_bk_delay))
    pt_tickers = Thread(target=poll_tickers, args=(run_event, market, tick_delay))
    pt_trades = Thread(target=poll_trades, args=(run_event, market, trades_delay))

    pt_orders = Thread(target=poll_orders, args=(run_event, orders_delay))
    pt_fills = Thread(target=poll_fills, args=(run_event, fills_delay))

    # ZipObj: { 'stream_channel(True/False)': "polling_threads" }
    stream_zips = list(zip(
        [stream_orderbook, stream_trades, stream_tickers, stream_fills, stream_orders],
        [pt_orderbook, pt_trades, pt_tickers, pt_fills, pt_orders]
    ))

    for starting in list(stream_zips):
        if not starting[0]:
            pass
        else:
            starting[1].start()
            time.sleep(0.5)
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:  # -IF-> KeyboardInterrupt[ctrl+C] -THEN-> disconnect.SysExit
        print(f'\n> Attempt -> Terminate_All_Active_Threads[ {enumerate_threads()} ]')
        run_event.clear()
        for stop in list(stream_zips):
            if stop[0]:
                stop[1].join()
                print(f'\n> TerminatingThread( <name[{stop[1].name}]> : <id[{stop[1].ident}]> )'
                      f'\n>> Thread({stop[1].name}).isAlive = {stop[1].is_alive()}')
    finally:
        print('>>> execute(Terminate_All_Active_Threads) = Successful_Failure')
        ws_client.disconnect()


if __name__ == '__main__':
    print(f'>>> Running FTX_ws_Worker as {__name__}')

    stream_wizard(
        market='BTC-PERP',
        stream_orderbook=True, ord_bk_delay=0.1,
        stream_tickers=True, tick_delay=0.5,
        stream_trades=True, trades_delay=3.5,
    )

else:
    print(f'>>> Running FTX_ws_Worker as {__name__}')

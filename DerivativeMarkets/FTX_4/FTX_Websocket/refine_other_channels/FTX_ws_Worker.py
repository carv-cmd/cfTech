# POLLING_USER_STATS: [polls_fills, polls_orders]
#
# import json
# import time
# from datetime import datetime
# from threading import Thread, Event, Lock
# from threading import enumerate as enumerate_threads
#
# from FTX_ws_Client import FtxWebsocketClient, Optional
#
# ws_client = FtxWebsocketClient()
# locker = Lock()
#
#
# def poll_writer(polling_channel: str, ts_daters: list):
#     """ TODO Generate docstring for poll_writer function """
#     global locker
#     locker.acquire()
#     print(f'\n* I/O_[{polling_channel}].LOCKED = [ {locker.locked()} ]')
#     try:
#         if not ts_daters[1]:
#             raise ValueError('>>> SKIPPED_EMPTY_SET')
#         with open(f'../temp_storage/{polling_channel}.txt', mode='a') as file_obj:
#             file_obj.writelines(f"{json.dumps({f'REFRESH_{polling_channel}': ts_daters[0]})}\n"
#                                 f"{json.dumps({f'UPDATED': ts_daters[1]})}\n", )
#     except Exception as exc:
#         print(f'\n*** <<WRITE_FAILED:[ {polling_channel} ]: [ {exc} ]>>')
#         raise
#     finally:
#         locker.release()
#         print(f'\n** I/O_[({polling_channel})] = [ {locker.locked()} ]')
#         return
#
#
# def foo_polls(func, ts, market, stream, delay, run_event: Event):
#     """
#     Continuously polls FTX market data streams -> ex = ws_client.get_tickers('BTC-PERP')
#     Called implicitly from stream_wizard, please ignore. . .
#     :param func: FTX_ws_Client.StreamMethod -> ws_client.get_orderbooks() == func()
#     :param ts: Timestamp -> either FTX[orderbook, tickers] or local[trades]
#     :param market: Name of the market to stream data from. -> market='BTC-PERP'
#     :param stream: Type/channel stream -> 'tickers', 'orderbook', etc
#     :param delay: Time to wait between polling the server.
#     :param run_event: Event loop object to sync with SystemExit
#     :return: Continuously writes to file or working_db.
#     """
#
#     valid_name = ''.join(['_' if x in '/' else x for x in market]).upper()
#     while run_event.is_set():
#         time.sleep(delay)
#         foo_writer = Thread(
#             target=poll_writer,
#             args=(f'{stream.upper()}_{valid_name}',
#                   [ts(market.upper()), func(market.upper())]))
#         foo_writer.start()
#
#
# def stream_wizard(market: str, *,
#                   orderbooks: Optional[float] = None,
#                   tickers: Optional[float] = None,
#                   trades: Optional[float] = None):
#     """
#     Call stream_wizard w/ stream_x(True) to establish websocket stream connection
#     Market names !required to pass as UPPERS, although good practice to do so anyway
#     :param market: FTX market to stream from; ex( "BTC-PERP" or "BTC/USDT")
#     :param orderbooks: Stream FTX orderbooks. Pass 'poll delay' as float to initialize.
#     :param tickers: Stream FTX tickers. Pass 'poll delay' as float to initialize.
#     :param trades: Stream FTX trades. Pass 'poll delay' as float to initialize.
#     :return: "Concurrently" writes files to working_db or disk for testing
#     """
#
#     run_event = Event()
#     run_event.set()
#     streamers = {
#         'orderbook': [orderbooks, ws_client.get_orderbook, ws_client.get_orderbook_timestamp],
#         'ticker': [tickers, ws_client.get_ticker, ws_client.get_ticker_timestamp],
#         'trade': [trades, ws_client.get_trades, datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')]
#     }
#
#     halt_streams = []
#     for stream, subs in streamers.items():
#         if subs[0] is not None:
#             func, ts, delay = subs[1], subs[2], subs[0]
#             polling_thread = Thread(target=foo_polls,
#                                     args=(func, ts, market, stream, delay, run_event))
#             polling_thread.start()
#             halt_streams.append(polling_thread)
#             time.sleep(0.5)
#
#     try:
#         while 1:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print(f'\n> Attempt -> Terminate_All_Active_Threads[ {enumerate_threads()} ]')
#         run_event.clear()
#         for stopper in halt_streams:
#             stopper.join()
#             print(f'\n>> Thread(<name[{stopper.name}]>:<id[{stopper.ident}]>).isAlive '
#                   f'= {stopper.is_alive() is False}')
#     finally:
#         print('>>>> Terminated_All_Polling_Threads -> raising SystemExit')
#         ws_client.disconnect()
#     return
#
#
# if __name__ == '__main__':
#     print(f'>>> Running FTX_ws_Worker as {__name__}')
#     stream_wizard('BTC-PERP', orderbooks=2, tickers=3)
#
# else:
#     print(f'>>> Running FTX_ws_Worker as {__name__}')

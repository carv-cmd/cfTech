# import json
# import time
# from threading import Thread, Event, Lock
# from threading import enumerate as enumerate_threads
#
# from FTX_ws_Client import FtxWebsocketClient, Dict, Sequence, Tuple
#
# __all__ = ['StreamWizard', 'Thread', 'Event', 'Lock', 'enumerate_threads']
#
#
# class StreamWizard(FtxWebsocketClient):
#
#     def __init__(self):
#         super().__init__()
#         self._locks = Lock()
#         self._run_event = Event()
#         self._get_streams = dict(
#             orderbook=[self.get_orderbook, self.get_orderbook_timestamp],
#             ticker=[self.get_ticker, self.get_ticker_timestamp],
#             trades=[self.get_trades, self.curr_time]
#         )
#
#     @staticmethod
#     def format_entries(polling: Sequence[Tuple[str, Tuple[float, ...]]]):
#         return [(mkt[0],
#                  {x: y for x, y in list(zip(['orderbook', 'ticker', 'trades'], [*mkt[1]]))})
#                 for mkt in polling]
#
#     def _stream_writer(self, polling_channel: str, time_series_data: list):
#         self._locks.acquire()
#         print(f'\n>>FILE.I/O.WRITE({polling_channel}).locked={self._locks.locked()}')
#         try:
#             if not time_series_data[1]:
#                 print(f'>>> SKIPPED_NULL: {polling_channel} >>>')
#                 raise ValueError(f'>>> SKIPPED_WRITE_TIME[<{time_series_data[0]}>')
#             with open(f'../temp_storage/{polling_channel}.txt', mode='a') as file_obj:
#                 file_obj.writelines(
#                     f"{json.dumps({f'REFRESH_{polling_channel}': time_series_data[0]})}\n"
#                     f"{json.dumps({f'UPDATED': time_series_data[1]})}\n")
#         except Exception as exc:
#             print(f'\n>>> FILE.I/O.FAIL:[ {polling_channel} : {exc} ]')
#             raise
#         finally:
#             self._locks.release()
#             print(f'\n>>> FILE.I/O.locked = {self._locks.locked()}')
#             return
#
#     def _thread_wizard(self, func, ts, market, stream, delay):
#         file_name = ''.join(['_' if x in '/' else x for x in market]).upper()
#         while self._run_event.is_set():
#             time.sleep(delay)
#             safe_write = Thread(
#                 target=self._stream_writer,
#                 args=(f'{stream.upper()}_{file_name}',
#                       [ts(market.upper()), func(market.upper())]))
#             safe_write.start()
#
#     def _stream_wizard(self, args):
#         self._run_event.set()
#         halter = []
#         for streams in args:
#             for market, metrics in streams:
#                 for channels, delay in metrics.items():
#                     sub_func, ts = self._get_streams[channels]
#                     stream_threader = Thread(
#                         target=self._thread_wizard,
#                         args=(sub_func, ts, market, channels, delay))
#                     stream_threader.start()
#                     halter.append(stream_threader)
#                     time.sleep(0.5)
#         try:
#             while 1:
#                 time.sleep(1)
#         except KeyboardInterrupt:
#             print(f'\n>>>> TRY: Terminate_All:[ {enumerate_threads()} ]')
#             self._run_event.clear()
#             for stopper in halter:
#                 stopper.join()
#                 time.sleep(0.25)
#         finally:
#             print('\n>>>> Terminated_All_Polling_Threads -> raises SystemExit')
#             self.disconnect()
#         return
#
#     def _one_stream_wizard(self, subscribe_to):
#         self._stream_wizard([subscribe_to])
#
#     def _many_stream_wizards(self, subs_sets: Sequence[Tuple[str, Tuple[float, ...]]]):
#         self._one_stream_wizard(self.format_entries(subs_sets))
#
#     def single_market(self, subscribe_one: Tuple[str, Dict[str, float]]):
#         """ ( 'market_name', {'orderbook': float, 'ticker': float, 'trades': float} ) """
#         self._one_stream_wizard([subscribe_one])
#
#     def multi_market(self, subs_many: Sequence[Tuple[str, Tuple[float, ...]]]):
#         """ [ ('market_name', (float(orderbook), float(ticker), float(trades))), ... ] """
#         self._many_stream_wizards(subs_many)
#
#
# if __name__ == '__main__':
#     print(f'>>> Running FTX_ws_WorkerClass as {__name__}')
#     chan = (1.0, 1.0)
#     degeneracy = [
#         ('BTC-PERP', chan), ('BTC/USD', chan), ('BTC/USDT', chan), ('BTC/TRYB', chan),
#         ('ETH-PERP', chan), ('ETH/USD', chan), ('ETH/USDT', chan)
#     ]
#     ftx = StreamWizard()
#     ftx.multi_market(degeneracy)
#
# else:
#     print(f'>>> Running FTX_ws_WorkerClass as {__name__}')
#     StreamWizard = StreamWizard

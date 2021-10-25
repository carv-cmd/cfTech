# from bsonjs import dumps as js_dumps
# from bsonjs import loads as bs_loads
# from bson.json_util import loads as mon_loads
# from bson.json_util import CANONICAL_JSON_OPTIONS
# import codecs
# from struct import Struct, error
# from bson.json_util import loads as mon_loads
# import sys
# import aiodns
# from datetime import datetime
import os
import logging
import time
import asyncio
import tracemalloc
from asyncio import queues
from typing import Dict, List

# from aioTraceConfig import RequestTracing
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)

tracemalloc.start()


__all__ = ['AioHttpREST']


class _RootRequest:

    _X_LIMIT = 29
    _Co = "\033[38;5;{}m{}"

    def __init__(self):
        super(_RootRequest, self).__init__()
        self._ev_loop = asyncio.get_event_loop()
        self._session = None
        self._base_url = None
        self._api_key = None
        self._packaged = None
        self._response_queue = None

    @property
    def ev_loop(self):
        logger.info(self._Co.format('14', f"* <<EVENT_LOOP[started]>>"))
        return self._ev_loop

    @property
    def session(self) -> ClientSession:
        # logger.info(f'* <<return:SESSION:[{self._session}]>>')
        return self._session

    @session.setter
    def session(self, value):
        self._session = value
        logger.info(self._Co.format('14', f'* <<set:SESSION:[{self._session}]>>\n'))

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def api_key(self) -> Dict:
        return {'api_key': os.getenv(self._api_key)}

    @property
    def packaged(self) -> List:
        return self._packaged

    @property
    def response_queue(self) -> queues.PriorityQueue:
        return self._response_queue

    @base_url.setter
    def base_url(self, value: str):
        logger.info(self._Co.format('14', f'* <<URL.SET[{value}]>>'))
        self._base_url = value

    @api_key.setter
    def api_key(self, value: str):
        logger.info(self._Co.format('14', f"* <<API_KEY.SET[{value}]>>"))
        self._api_key = value

    @packaged.setter
    def packaged(self, value: list):
        assert self._base_url is not None
        _root_idx = self._base_url
        endpt_array = [f"{_root_idx}/{idx[0]}/{idx[1]}" for idx in value]
        try:
            _total_len = len(endpt_array)
            assert _total_len > self._X_LIMIT, 'ArrayLength < X-limit; ignore'
            self._packaged = self.divisor(endpt_array, _total_len, self._X_LIMIT)
        except AssertionError:
            self._packaged = [endpt_array]

    @response_queue.setter
    def response_queue(self, value):
        self._response_queue = value

    @staticmethod
    def divisor(_total, _total_len, _xim):
        _total_copy = _total.copy()
        _x_lim = divmod(_total_len, _xim)[0]
        _total = [[_total_copy.pop() for _r1 in range(_xim)] for _ in range(_x_lim)]
        if _total_copy:
            _total.append(_total_copy)
        return _total


class AioHttpREST(_RootRequest):

    def __init__(self):
        super(AioHttpREST, self).__init__()
        self._counter = time.perf_counter
        self.response_queue = queues.LifoQueue()

    def set_basis(self, base_url: str, base_key: str):
        if base_url is not self.base_url:
            self.base_url = base_url
        if (base_key is not None) and (base_key is not self.api_key):
            self.api_key = base_key
        assert self.base_url and self.api_key is not None, \
            AttributeError("ValidateBasis")

    def terminate_session(self):
        async def terminator(session: ClientSession):
            await session.close()
            logger.info(self._Co.format('15', f">>> Terminator['SessionClosed']={self.session.closed}"))
        try:
            asyncio.run(terminator(self.session))
        except Exception as exp:
            logger.info(f'TerminateSessionRaised: {exp}')

    async def _fill_pool(self):
        if self.session is None:
            self.session = ClientSession()

    async def _async_io(self, url_path: str, pars: dict, _aki: dict):
        """
        AIO_Request.get() method.
        Global session pooling, terminate.wait_for(sysExit)

        :param url_path: Absolute path to API endpoint
        :param pars: Request parameters
        :param _aki: api_key/PAIR(set by parent)
        :return: None
        """
        async with self.session.get(url_path, params={**pars, **_aki}, chunked=True) as respo:
            # try:
            #     respo.raise_for_status()
            #     _start = datetime.now()
            #     _resp_pkg = bytearray(b"")
            #     # TODO is 'iter_chunked(4096 * 4096)' faster???
            #     async for _chunk in respo.content.iter_any():
            #         _resp_pkg += memoryview(_chunk).tobytes()
            #     _proc_time = (datetime.now() - _start).total_seconds()
            #     logger.info(f'-> stream.TIME({url_path} == <{_proc_time}sec>)')
            #     _resp_pkg = memoryview(_resp_pkg)
            # except ClientResponseError:
            #     _4xx_schema = ['URL', 'Status', 'Header']
            #     _no_good = (str(respo.url), f"<{respo.status}:{respo.reason}>", dict(respo.headers))
            #     _resp_pkg = [(*_bad,) for _bad in zip(_4xx_schema, _no_good)]
            #     logger.warning(f'-> BAD_REQUEST({url_path})')
            # except Exception as exr:
            #     logger.warning(repr(exr))
            # finally:
            #     return _resp_pkg
            _signature = (url_path.split('/')[-2:], pars)
            _start = self._counter()

            try:
                respo.raise_for_status()
                _resp_pkg, _chunk_count = bytearray(b""), 0
                async for _chunk in respo.content.iter_chunked(4096 * 4096):
                    # logger.info(self._Co.format('201', f'>>> BUFFERING({url_path})'))
                    _resp_pkg += memoryview(_chunk).tobytes()
                    _chunk_count += 1

                _proc_time = (self._counter() - _start)
                _stats = f"> [ CHUNKS:<#{_chunk_count}> | TIME:<{_proc_time}> | URL=?{url_path} ]"
                logger.info(self._Co.format('14', _stats))
                self.response_queue.put_nowait((_signature, memoryview(_resp_pkg)))

            except ClientResponseError:
                _4xx_schema = ['URL', 'Status', 'Header']
                _no_good = (str(respo.url), f"<{respo.status}:{respo.reason}>", dict(respo.headers))
                logger.info(self._Co.format('196', f"-> BAD_REQUEST({_no_good[1]})[{url_path}]"))
                self.response_queue.put_nowait(
                    (_signature, [(*_bad,) for _bad in zip(_4xx_schema, _no_good)]))

    async def _aio_arbiter(self, params: dict, _x_lim_wait=65.0):
        """
        AioHttpREST[producer|consumer] arbiter function.
        :param params: Request parameters
        :param _x_lim_wait: One minute wait for request-X-limit reset.
        """
        await self._fill_pool()
        _key = self.api_key
        _tasks = [asyncio.create_task(self.aio_queue()) for _ in range(3)]

        for _idx, _groups in enumerate(self.packaged):
            if _idx > 0:
                logger.info(self._Co.format('15', f'*-> X-Limit.sleep({_x_lim_wait})\n'))
                await asyncio.sleep(_x_lim_wait)

            _start = self._counter()
            _requester = (
                asyncio.create_task(self._async_io(_target, params, _key)) for _target in _groups
            )
            await asyncio.gather(*_requester, return_exceptions=True)

            logger.info(self._Co.format('196', f'>>> BATCH.TIME(<{(self._counter() - _start)}>)'))
            await self.aio_writer(params)

        await self.response_queue.join()
        for tasked in _tasks:
            tasked.cancel()

        await asyncio.gather(*_tasks, return_exceptions=True)

    def pooled_aio(self, endpoints: list, parameters: dict, base_url: str = None, base_key: str = None):
        if base_url:
            self.set_basis(base_url, base_key)
        self.packaged = endpoints
        self.ev_loop.run_until_complete(self._aio_arbiter(parameters))

    async def aio_queue(self) -> None:
        """
        Request(memoryview's & BadRequest) responses placed in queue.\n
        Implement child class w/ queue handler to retrieve responses.
        """
        while True:
            _signature, _response = await self.response_queue.get()
            logger.info(f'>>> Queue Signature: {_signature}')

    async def aio_writer(self, parameters: dict) -> None:
        """
        Inline response writer.\n
        NOTE: Assumes correlation between request parameters and collection names.\n
        :param parameters: Request parameters.
        """
        pass

    # async def _json_aio_requester(self, url_path: str, pars: dict, _aki: dict):
    #     """
    #     AIO_Request.get() method.
    #     Global session pooling, terminate.wait_for(sysExit)
    #
    #     :param url_path: Absolute path to API endpoint
    #     :param pars: Request parameters
    #     :param _aki: api_key/PAIR(set by parent)
    #     :return: None
    #     """
    #     async with self.session.get(url_path, params={**pars, **_aki}) as resp:
    #         _start = datetime.now()
    #         try:
    #             resp.raise_for_status()
    #             _resp_obj = await resp.json(content_type=None)
    #             _ended = (datetime.now() - _start).total_seconds()
    #             logger.info(f'-> jBson.TIME(<{_ended}>) -> {url_path}')
    #         except ClientResponseError:
    #             _4xx_schema = ['URL', 'Status', 'Header']
    #             _no_good = [str(resp.url), f"<{resp.status}:{resp.reason}>", dict(resp.headers)]
    #             _resp_obj = [(*_bad,) for _bad in zip(_4xx_schema, _no_good)]
    #             logger.info(f'-- RECV:4xx:?{url_path}')
    #         return _resp_obj

    # async def _async_aio(self, url_path: str, pars: dict, _aki: dict):
    #     """
    #     AIO_Request.get() method.
    #     Global session pooling, terminate.wait_for(sysExit)
    #
    #     :param url_path: Absolute path to API endpoint
    #     :param pars: Request parameters
    #     :param _aki: api_key/PAIR(set by parent)
    #     :return: None
    #     """
    #     async with self.session.get(url_path, params={**pars, **_aki}, chunked=True) as respo:
    #         # try:
    #         #     respo.raise_for_status()
    #         #     _start = datetime.now()
    #         #     _resp_pkg = bytearray(b"")
    #         #     # TODO is 'iter_chunked(4096 * 4096)' faster???
    #         #     async for _chunk in respo.content.iter_any():
    #         #         _resp_pkg += memoryview(_chunk).tobytes()
    #         #     _proc_time = (datetime.now() - _start).total_seconds()
    #         #     logger.info(f'-> stream.TIME({url_path} == <{_proc_time}sec>)')
    #         #     _resp_pkg = memoryview(_resp_pkg)
    #         # except ClientResponseError:
    #         #     _4xx_schema = ['URL', 'Status', 'Header']
    #         #     _no_good = (str(respo.url), f"<{respo.status}:{respo.reason}>", dict(respo.headers))
    #         #     _resp_pkg = [(*_bad,) for _bad in zip(_4xx_schema, _no_good)]
    #         #     logger.warning(f'-> BAD_REQUEST({url_path})')
    #         # except Exception as exr:
    #         #     logger.warning(repr(exr))
    #         # finally:
    #         #     return _resp_pkg
    #         try:
    #             respo.raise_for_status()
    #             _start = self._counter()
    #             _chunk_counter = 0
    #             _resp_pkg = bytearray(b"")
    #             async for _chunk in respo.content.iter_any():
    #                 # logger.info(self._Co.format('11', f'>>> BUFFERING({url_path})'))
    #                 _resp_pkg += memoryview(_chunk).tobytes()
    #                 _chunk_counter += 1
    #             _proc_time = (self._counter() - _start)
    #             _stats = f"> [ chunks:<{_chunk_counter}> | time:<{_proc_time}> ]:?{url_path}\n"
    #             logger.info(self._Co.format('200', _stats))
    #             # return memoryview(_resp_pkg)
    #             await self.response_queue.put(memoryview(_resp_pkg))
    #         except ClientResponseError:
    #             _4xx_schema = ['URL', 'Status', 'Header']
    #             _no_good = (str(respo.url), f"<{respo.status}:{respo.reason}>", dict(respo.headers))
    #             logger.warning(self._Co.format('196', f"-> BAD_REQUEST({url_path})"))
    #             return [(*_bad,) for _bad in zip(_4xx_schema, _no_good)]
    #
    # async def _aio_arbiter(self, params: dict, _key: dict, x_lim_wait=0.0):
    #     """
    #     :param params: Request parameters
    #     :param _key: API_KEY environment variable string
    #     :param x_lim_wait: X-request-limit.sleep(60sec)
    #     :return: None
    #     """
    #     await self._fill_pool()
    #     for _idx, _grouping in enumerate(self.packaged):
    #         if _idx > 0:
    #             self._x_lim_wait = 65.0
    #         _start = self._counter()
    #         _reqs = [asyncio.create_task(self._async_aio(_target, params, _key)) for _target in _grouping]
    #         # _requests = (self._json_aio_requester(_target, params, _key) for _target in _grouping)
    #         _result = await asyncio.gather(*_reqs, loop=self.ev_loop, return_exceptions=True)
    #         # await self.response_queue.put((_result, params))
    #         logger.info(self._Co.format('11', f'>>> BATCH.TIME(<{(self._counter() - _start)}>)\n'))
    #         await self.aio_writer(_grouping, params, x_lim_wait)
    #     await self.response_queue.join()
    #
    # def pooled_aio(self, endpoints: list, parameters: dict, base_url: str = None, base_key: str = None):
    #     if base_url:
    #         self.set_basis(base_url, base_key)
    #     self.packaged = endpoints
    #     _readied_tuple = (parameters, self.api_key)
    #     self.ev_loop.run_until_complete(self._aio_arbiter(*_readied_tuple))
    #     # self.ev_loop.run_until_complete(asyncio.gather(self._aio_arbiter(*_readied_tuple)))
# async def _async_aio(self, url_path: str, pars: dict, _aki: dict, _idx: int):
    #     """
    #     AIO_Request.get() method.
    #     Global session pooling, terminate.wait_for(sysExit)
    #
    #     :param url_path: Absolute path to API endpoint
    #     :param pars: Request parameters
    #     :param _aki: api_key/PAIR(set by parent)
    #     :return: None
    #     """
    #     async with self.session.get(url_path, params={**pars, **_aki}, chunked=True) as respo:
    #         # async for _chunk in respo.content.iter_chunked(4096 * 4096):
    #         logger.info(f'>>> RequestURL: {url_path}')
    #         try:
    #             _start = datetime.now()
    #             respo.raise_for_status()
    #             _resp_pkg = bytearray(b"")
    #             async for _chunk in respo.content.iter_any():
    #                 _resp_pkg += _chunk
    #             self.response_queue.append(_resp_pkg)
    #             logger.info(f'-> stream.TIME(<{(datetime.now() - _start).total_seconds()}>)')
    #         except ClientResponseError:
    #             _4xx_schema = ['URL', 'Status', 'Header']
    #             _no_good = [str(respo.url), f"<{respo.status}:{respo.reason}>", dict(respo.headers)]
    #             _resp = [(*_bad,) for _bad in zip(_4xx_schema, _no_good)]
    #             self.response_queue.append(_resp)
    #             logger.info(f'-> stream.TIME(<BadRequest:4xx>)')
    #         except Exception as exr:
    #             print(repr(exr))
    #
    # async def _aio_arbiter(self, params: dict, _key: dict, x_lim_wait=62.0):
    #     """
    #     :param params: Request parameters
    #     :param _key: API_KEY environment variable string
    #     :param x_lim_wait: X-request-limit.sleep(60sec)
    #     :return: None
    #     """
    #     _start = datetime.now()
    #     await self._fill_pool()
    #     _pkg_len = len(self.packaged) - 1
    #     for _idx, _grouping in enumerate(self.packaged):
    #         if _idx == _pkg_len:
    #             x_lim_wait = 0.0
    #         _test = [self._async_aio(_target, params, _key, _idx) for _target in _grouping]
    #         for _target in _grouping:
    #             # await self._json_aio_requester(_target, params, _key)
    #             await self._async_aio(_target, params, _key, _idx)
    #         logger.info(f'>>> BATCH.TIME(<{(datetime.now() - _start).total_seconds()}>)')
    #         await self.aio_writer(self.response_queue, _grouping, params, x_lim_wait)
    #     logger.info(f"* Interim['SessionClosed']={self.session.closed}\n")
if __name__ == '__main__':
    try:
        pass
    except Exception as e:
        raise e

# class RootRequest:
#
#     # __slots__ = ('_ev_loop', '_base_url', '_packaged', '_session', '_api_key')
#
#     def __init__(self):
#         super(RootRequest, self).__init__()
#         self._ev_loop = asyncio.get_event_loop()
#         self._base_url = None
#         self._packaged = None
#         self._session = None
#         self._api_key = None
#
#     @property
#     def ev_loop(self):
#         logger.info("* <<EVENT_LOOP[started]>>")
#         return self._ev_loop
#
#     @property
#     def base_url(self):
#         return self._base_url
#
#     @base_url.setter
#     def base_url(self, value):
#         logger.info(f'* <<URL.SET[{value}]>>')
#         self._base_url = value
#
#     @property
#     def packaged(self):
#         return self._packaged
#
#     @packaged.setter
#     def packaged(self, value: tuple):
#         self._packaged = value
#
#     @packaged.deleter
#     def packaged(self):
#         logger.info(f'<DELETE> ')
#         del self._packaged
#
#     @property
#     def session(self):
#         return self._session
#
#     @session.setter
#     def session(self, value):
#         logger.info(f'* <<SESSION.SET[{value}]>>\n')
#         self._session = value
#
#     @property
#     def api_key(self) -> Dict:
#         return self._api_key
#
#     @api_key.setter
#     def api_key(self, value: str):
#         logger.info(f'* <<API_KEY.SET[{value}]>>')
#         self._api_key = {'api_key': os.getenv(value)}
#
#
# class PkgRequests(RootRequest):
#
#     def divisor(self, _total, _total_len, _xim):
#         try:
#             _total_copy = _total.copy()
#             _x_lim = divmod(_total_len, _xim)[0]
#             _total = [[_total_copy.pop() for _r1 in range(_xim)] for _ in range(_x_lim)]
#             if _total_copy:
#                 _total.append(_total_copy)
#             self.packaged = _total
#         except Exception as edx:
#             raise edx
#
#     def package_requests(self, endpt_array: list, x_lim: int = 2):
#         assert self.base_url is not None
#         _root_idx = self.base_url
#         endpt_array = [f"{_root_idx}/{idx}/{endpt}" for idx, endpt in endpt_array]
#         try:
#             _total_len = len(endpt_array)
#             assert _total_len > x_lim, 'ArrayLength < X-limit; ignore'
#             self.divisor(endpt_array, _total_len, x_lim)
#         except AssertionError:
#             self.packaged = [endpt_array]
#
#
# class AioHttpREST(PkgRequests):
#
#     # __slots__ = ('response_queue',)
#
#     def __init__(self):
#         super(AioHttpREST, self).__init__()
#         self.response_queue = list()
#
#     async def _fill_pool(self):
#         if self.session is None:
#             self.session = ClientSession()
#
#     async def _aio_requester(self, url_path: str, pars: dict, _aki: dict):
#         """
#         AIO_Request.get() method.
#         Global session pooling, terminate.wait_for(sysExit)
#
#         :param url_path: Absolute path to API endpoint
#         :param pars: Request parameters
#         :param _aki: api_key/PAIR(set by parent)
#         :return: None
#         """
#         async with self.session.get(url_path, params={**pars, **_aki}) as resp:
#             _stats = (str(resp.url), resp.status, resp.reason, dict(resp.headers))
#             try:
#                 assert _stats[1] == 200
#                 _temps = await resp.json(content_type=None)
#                 self.response_queue.append(_temps)
#             except AssertionError:
#                 _4xx_schema = ['URL', 'Status', 'Header']
#                 _no_good = [_stats[0], f"<{_stats[1]}:{_stats[2]}>", _stats[3]]
#                 _resp = [(*_bad,) for _bad in zip(_4xx_schema, _no_good)]
#                 self.response_queue.append(_resp)
#
#     async def _aio_arbiter(self, params: dict, _key: dict, x_lim_wait: float = 4.0):
#         """
#         AIO.session pooling arbiter.
#
#         :param params: Request parameters
#         :param _key: API_KEY environment variable string
#         :param x_lim_wait: X-request-limit.sleep(60sec)
#         :return: None
#         """
#         await self._fill_pool()
#         _pkg_len = len(self.packaged) - 1
#         for _idx, _grouping in enumerate(self.packaged):
#             if _idx == _pkg_len:
#                 x_lim_wait = 0.0
#             for _target in _grouping:
#                 await self._aio_requester(_target, params, _key)
#             await self.aio_writer(self.response_queue, _grouping, params, x_lim_wait)
#         logger.info(f"* Interim['SessionClosed']={self.session.closed}\n")
#
#     def terminate_session(self):
#         async def terminator(session: ClientSession):
#             assert not session.closed, '!pool instance to flush'
#             await session.close()
#             logger.info(f">>> Terminator['SessionClosed']={self.session.closed}")
#         self.ev_loop.run_until_complete(terminator(self.session))
#
#     def set_basis(self, base_url: str, base_key: str):
#         if base_url is not self.base_url:
#             self.base_url = base_url
#         if (base_key is not None) and (base_key is not self.api_key):
#             self.api_key = base_key
#         assert self.base_url and self.api_key is not None, \
#             f"AssertBases(<{self.base_url}>, <{self.api_key}>)"
#
#     def pooled_aio(
#         self,
#         endpoints: list,
#         parameters: dict,
#         base_url: str = None,
#         base_key: str = None,
#     ):
#         if base_url:
#             self.set_basis(base_url, base_key)
#         self.package_requests(endpoints)
#         _readied_tuple = (parameters, self.api_key)
#         self.ev_loop.run_until_complete(self._aio_arbiter(*_readied_tuple))
#
#     async def aio_writer(self, write_data: list, grouping: list, params: dict, x_lim: float):
#         raise NotImplementedError()

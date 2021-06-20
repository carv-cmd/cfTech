# from bson.json_util import loads as loads_bson
# from bson.json_util import dumps as dumps_bson
# from bsonjs import loads as js_loads
# from bsonjs import dumps as js_dumps
import os
import logging
from typing import Dict
from aiohttp import ClientSession
import tracemalloc
import asyncio
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
logging.basicConfig(level=logging.INFO, format='(%(threadName)-9s) %(message)s')
tracemalloc.start()


__all__ = ['RootRequest', 'AioHttpREST']


class RootRequest:

    # __slots__ = ('_ev_loop', '_base_url', '_packaged', '_session', '_api_key')

    _X_LIMIT = 2

    def __init__(self):
        super(RootRequest, self).__init__()
        self._ev_loop = asyncio.get_event_loop()
        self._base_url = None
        self._packaged = None
        self._session = None
        self._api_key = None

    @staticmethod
    def divisor(_total, _total_len, _xim):
        _total_copy = _total.copy()
        _x_lim = divmod(_total_len, _xim)[0]
        _total = [[_total_copy.pop() for _r1 in range(_xim)] for _ in range(_x_lim)]
        if _total_copy:
            _total.append(_total_copy)
        return _total

    @property
    def ev_loop(self):
        logging.info("* <<EVENT_LOOP[started]>>")
        return self._ev_loop

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def packaged(self) -> list:
        return self._packaged

    @property
    def session(self) -> ClientSession:
        return self._session

    @session.setter
    def session(self, value):
        if self._session is None:
            self._session = value

    @property
    def api_key(self) -> Dict:
        return self._api_key

    @base_url.setter
    def base_url(self, value):
        logging.info(f'* <<URL.SET[{value}]>>')
        self._base_url = value

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

    @session.setter
    def session(self, value):
        logging.info(f'* <<SESSION.SET[{value}]>>\n')
        self._session = value

    @api_key.setter
    def api_key(self, value: str):
        logging.info(f'* <<API_KEY.SET[{value}]>>')
        self._api_key = {'api_key': os.getenv(value)}

    @packaged.deleter
    def packaged(self):
        # logging.info(f'<DELETE> ')
        del self._packaged


class AioHttpREST(RootRequest):

    # __slots__ = ('response_array',)

    def __init__(self):
        super(AioHttpREST, self).__init__()
        self.response_array = list()
        # self.x_lim_wait = 10.0

    def terminate_session(self):
        async def terminator(session: ClientSession):
            assert not session.closed, '!pool instance to flush'
            await session.close()
            logging.info(f">>> Terminator['SessionClosed']={self.session.closed}")
        try:
            self.ev_loop.run_until_complete(terminator(self.session))
        except AssertionError:
            pass

    async def _fill_pool(self):
        if self.session is None:
            self.session = ClientSession()

    async def _aio_requester(self, url_path: str, pars: dict, _aki: dict):
        """
        AIO_Request.get() method.
        Global session pooling, terminate.wait_for(sysExit)

        :param url_path: Absolute path to API endpoint
        :param pars: Request parameters
        :param _aki: api_key/PAIR(set by parent)
        :return: None
        """
        async with self.session.get(url_path, params={**pars, **_aki}) as resp:
            _stats = (str(resp.url), resp.status, resp.reason, dict(resp.headers))
            try:
                assert _stats[1] == 200
                _temps = await resp.json(content_type=None)
                self.response_array.append(_temps)
                logging.info(f'RECV:200:?{url_path}')
            except AssertionError:
                _4xx_schema = ['URL', 'Status', 'Header']
                _no_good = [_stats[0], f"<{_stats[1]}:{_stats[2]}>", _stats[3]]
                _resp = [(*_bad,) for _bad in zip(_4xx_schema, _no_good)]
                self.response_array.append(_resp)
                logging.info(f'RECV:4xx:?{url_path}')

    async def _aio_arbiter(self, params: dict, _key: dict, x_lim_wait=10.0):
        """
        AIO.session pooling arbiter.

        :param params: Request parameters
        :param _key: API_KEY environment variable string
        # :param x_lim_wait: X-request-limit.sleep(60sec)
        :return: None
        """
        await self._fill_pool()
        _pkg_len = len(self.packaged) - 1
        for _idx, _grouping in enumerate(self.packaged):
            if _idx == _pkg_len:
                x_lim_wait = 0.0
            for _target in _grouping:
                await self._aio_requester(_target, params, _key)
            await self.aio_writer(self.response_array, _grouping, params, x_lim_wait)
        logging.info(f"* Interim['SessionClosed']={self.session.closed}\n")

    def set_basis(self, base_url: str, base_key: str):
        if base_url is not self.base_url:
            self.base_url = base_url
        if (base_key is not None) and (base_key is not self.api_key):
            self.api_key = base_key
        assert self.base_url and self.api_key is not None, \
            AttributeError("ValidateBases")

    def pooled_aio(self, endpoints: list, parameters: dict, base_url: str = None, base_key: str = None):
        if base_url:
            self.set_basis(base_url, base_key)
        self.packaged = endpoints
        _readied_tuple = (parameters, self.api_key)
        self.ev_loop.run_until_complete(self._aio_arbiter(*_readied_tuple))
        del self.packaged

    async def aio_writer(self, write_data: list, grouping: list, params: dict, x_lim_wait: float):
        raise NotImplementedError()


if __name__ == '__main__':
    from pprint import pprint
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
#         logging.info("* <<EVENT_LOOP[started]>>")
#         return self._ev_loop
#
#     @property
#     def base_url(self):
#         return self._base_url
#
#     @base_url.setter
#     def base_url(self, value):
#         logging.info(f'* <<URL.SET[{value}]>>')
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
#         logging.info(f'<DELETE> ')
#         del self._packaged
#
#     @property
#     def session(self):
#         return self._session
#
#     @session.setter
#     def session(self, value):
#         logging.info(f'* <<SESSION.SET[{value}]>>\n')
#         self._session = value
#
#     @property
#     def api_key(self) -> Dict:
#         return self._api_key
#
#     @api_key.setter
#     def api_key(self, value: str):
#         logging.info(f'* <<API_KEY.SET[{value}]>>')
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
#     # __slots__ = ('response_array',)
#
#     def __init__(self):
#         super(AioHttpREST, self).__init__()
#         self.response_array = list()
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
#                 self.response_array.append(_temps)
#             except AssertionError:
#                 _4xx_schema = ['URL', 'Status', 'Header']
#                 _no_good = [_stats[0], f"<{_stats[1]}:{_stats[2]}>", _stats[3]]
#                 _resp = [(*_bad,) for _bad in zip(_4xx_schema, _no_good)]
#                 self.response_array.append(_resp)
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
#             await self.aio_writer(self.response_array, _grouping, params, x_lim_wait)
#         logging.info(f"* Interim['SessionClosed']={self.session.closed}\n")
#
#     def terminate_session(self):
#         async def terminator(session: ClientSession):
#             assert not session.closed, '!pool instance to flush'
#             await session.close()
#             logging.info(f">>> Terminator['SessionClosed']={self.session.closed}")
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

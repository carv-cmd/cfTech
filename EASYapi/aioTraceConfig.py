import logging.config
import asyncio
import tracemalloc
from aiohttp import TraceConfig
from collections import defaultdict
# from collections.abc import MutableMapping


__all__ = ['RequestTrace']

tracemalloc.start()


def start_logger(log_lvl: str):
    _TRACER = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "TRACING": {
                'format': "\033[38;5;196m[ <{name}> | <{asctime}> ]: \033[38;5;14m{message}",
                "style": '{'
            },
            "SAVING": {
                'format': "[ <{name}> | <{asctime}> ]: {message}",
                "style": '{'
            },
        },
        "handlers": {
            "consoleTracing": {
                "level": 'DEBUG',
                "class": 'logging.StreamHandler',
                "formatter": 'TRACING'
            },
            'fileSave': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': r'C:\Users\benca\PycharmProjects\cfTech\EASYapi\aioLogs.log',
                'formatter': 'SAVING'
            },
        },
        "loggers": {
            __name__: {
                'level': log_lvl.upper(),
                'handlers': ['consoleTracing', 'fileSave'],
                'propagate': True
            }
        }
    }
    logging.config.dictConfig(_TRACER)
    return logging.getLogger(__name__)


logger = start_logger('INFO')


class RequestTrace:
    def __init__(self):
        self._results = defaultdict(lambda x: x)

    def __call__(self):
        _on_start = asyncio.get_running_loop().time()
        _curr_time = asyncio.get_running_loop().time
        _redirected = False

        async def on_request_start(session, context, params):
            context.on_request_start = _on_start
            context.is_redirect = _redirected
            self._results['redirect'] = context.is_redirect

        async def on_request_redirect(session, context, params):
            context.on_request_redirect = _curr_time() - _on_start
            context.is_redirect = True
            self._results['redirect'] = context.is_redirect

        async def on_connection_create_start(session, context, params):
            context.on_connection_create_start = _curr_time() - _on_start

        async def on_dns_resolvehost_start(session, context, params):
            context.on_dns_resolvehost_start = _curr_time() - _on_start

        async def on_dns_resolvehost_end(session, context, params):
            context.on_dns_resolvehost_end = _curr_time() - _on_start

        async def on_connection_create_end(session, context, params):
            context.on_connection_create_end = _curr_time() - _on_start
            # return await context

        async def on_request_chunk_sent(session, context, params):
            context.on_request_chunk_sent = _curr_time() - _on_start

        async def on_request_end(session, context, params):
            final = _curr_time() - _on_start
            context.on_request_end = final
            try:
                _dns_look_n_dial = context.on_dns_resolvehost_end - context.on_dns_resolvehost_start
                _connection = context.on_connection_create_end - _dns_look_n_dial
            except AttributeError:
                _dns_look_n_dial = 'NULL'
                _connection = 'NULL'
            self._results['dns_lookup_and_dial'] = _dns_look_n_dial
            self._results['connect'] = _connection
            self._results['transfer'] = final - context.on_connection_create_end
            self._results['total'] = final
            _endpt = str(getattr(params, 'url')).split('/')[-2:]
            await self.build_tracer(_endpt, self._results)

        _tracer = TraceConfig()
        _tracer.on_request_start.append(on_request_start)
        _tracer.on_request_end.append(on_request_end)
        _tracer.on_request_redirect.append(on_request_redirect)
        _tracer.on_connection_create_start.append(on_connection_create_start)
        _tracer.on_connection_create_end.append(on_connection_create_end)
        _tracer.on_request_chunk_sent.append(on_request_chunk_sent)
        try:
            _tracer.on_dns_resolvehost_start.append(on_dns_resolvehost_start)
            _tracer.on_dns_resolvehost_end.append(on_dns_resolvehost_end)
        except Exception as etx:
            logger.warning(f'DNS.raised: {etx}')
        return _tracer

    async def build_tracer(self, endpt, _resi):
        _defi = defaultdict(lambda x: x.upper())
        _multiplier, _tup2 = 1000, 2
        for index in _resi:
            try:
                if index in 'is_redirect':
                    raise TypeError('is_redirect: bool')
                _defi[index] = f'{round(self._results[index] * _multiplier, _tup2)}'.zfill(3)
            except TypeError as e:
                _defi[index] = self._results[index]
        logger.info(f"{dict(_defi)} -> {endpt}")

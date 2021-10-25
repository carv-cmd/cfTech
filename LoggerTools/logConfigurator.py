import logging
from logging import config
from string import Template

__all__ = ['configure_logging']
# %(name)-9s whats the -9s for?


def configure_logging(mon_lvl: str = 'WARNING', aio_lvl: str = 'WARNING'):
    _std_logs = Template("$color[<{name}>|<{asctime}>]: {message}")
    _dtf = '%H:%M:%S'

    std_logs = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            'monFormat': {
                'format': _std_logs.substitute(color="\033[38;5;118m"),
                'datefmt': _dtf,
                'style': '{'
            },
            'restFormat': {
                'format': _std_logs.substitute(color="\033[38;5;105m"),
                'datefmt': _dtf,
                'style': '{'
            }
        },
        "handlers": {
            "monConsole": {
                "level": 'INFO',
                "class": 'logging.StreamHandler',
                "formatter": 'monFormat'
            },
            "restConsole": {
                "level": 'INFO',
                "class": 'logging.StreamHandler',
                "formatter": 'restFormat'
            },
            'fileHandle': {
                "level": 'INFO',
                "class": 'logging.StreamHandler',
                "formatter": 'restFormat'
            }
        },
        "loggers": {
            "MongoDatabase.monLoggers": {
                'handlers': ['monConsole'],
                'level': mon_lvl,
                'propagate': False
            },
            "EASYapi.RESTapi": {
                'handlers': ['restConsole'],
                'level': aio_lvl,
                'propagate': False
            },
        }
    }
    logging.config.dictConfig(std_logs)

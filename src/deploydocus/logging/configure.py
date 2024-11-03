import logging.config
from threading import Lock

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[%(levelname)-8s] - %(module)s:%(lineno)d - %(message)s"}
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
    },
    "root": {
        "level": "WARN",
        "handlers": [
            "stderr",
            "stdout",
            # "file"
        ],
    },
}

_set_logging = False
_lock = Lock()


def configure_logging():
    global _set_logging
    with _lock:
        if _set_logging:
            return
        else:
            logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)
            _set_logging = True

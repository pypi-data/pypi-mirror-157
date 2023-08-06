import logging
import os
from logging.config import dictConfig


class LOG_LEVEL:
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"


# NOTE: Log level can be set by environments, default is debug.
_level = os.environ.get("LOG_LEVEL", LOG_LEVEL.DEBUG)

LOG_FMT = (
    "[%(asctime)s.%(msecs)03d][%(levelname)s][pid%(process)d-tid%(thread)d]"
    + "[%(module)s][%(funcName)s:%(lineno)s]: %(message)s"
)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"standard": {"format": LOG_FMT, "datefmt": "%Y-%m-%dT%H:%M:%S"}},
    "handlers": {
        "default": {
            "level": _level,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        # Default root logger if omitted name
        "": {
            "handlers": ["default"],
            "level": _level,
            "propagate": False,
        },
    },
}

# NOTE: Run once at startup
dictConfig(LOGGING_CONFIG)


def get_logger():
    return logging.getLogger()

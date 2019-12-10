"""Logger object for the Flockwave server."""

import logging

from functools import partial
from typing import Any, Dict

from .formatters import styles

__all__ = ("add_id_to_log", "log", "install", "Logger", "LoggerWithExtraData")


Logger = logging.Logger

log = logging.getLogger(__name__.rpartition(".")[0])


class LoggerWithExtraData:
    """Object that provides the same interface as Python's standard logging
    functions, but automatically adds default values to the `extra` dict
    of each logging record.
    """

    def __init__(self, log: Logger, extra: Dict[str, Any]):
        """Constructor.

        Parameters:
            log: the logging module to wrap
            extra: extra data to add as default to each logging record
        """
        self._extra = dict(extra)
        self._log = log
        self._methods = {}

    def __getattr__(self, name):
        if name in self._methods:
            return self._methods
        else:
            wrapped_method = getattr(self._log, name)
            method = self._methods[name] = partial(self._call, wrapped_method)
            return method

    def _call(self, func, *args, **kwds):
        extra = kwds.get("extra") or self._extra

        if extra is not self._extra:
            for k, v in self._extra.items():
                if k not in extra:
                    extra[k] = v
        else:
            kwds["extra"] = self._extra

        return func(*args, **kwds)


def add_id_to_log(log: Logger, id: str):
    """Adds the given ID as a permanent extra attribute to the given logger.

    Parameters:
        log: the logger to wrap
        id: the ID attribute to add to the logger

    Returns:
        a new logger that extends the extra dict of each logging record with
        the given ID
    """
    return LoggerWithExtraData(log, {"id": id})


def create_formatter(style: str = "fancy"):
    """Creates a default log formatter according to the given style constant.

    Parameters:
        style: the style of the formatter; ``fancy`` shows a colorful output
            suitable for terminals, while ``plain`` shows a plain output that
            is suitable for logging in system logs
    """
    factory = styles.get(style, logging.Formatter)
    return factory()


def install(level: int = logging.INFO, style: str = "fancy"):
    """Install a default formatter and stream handler to the root logger of Python.

    This method can be used during startup to ensure that we can see the
    log messages on the console nicely.

    Parameters:
        level: the minimum logging level of messages that actually end up in the
            log
        style: the style of the formatter; see `create_formatter()` for details.
    """
    formatter = create_formatter(style)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    root_logger.addHandler(handler)
    root_logger.setLevel(level)

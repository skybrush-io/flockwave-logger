import logging

from typing import Any, Literal, Optional

from .hexdump import hexdump

__all__ = ("format_hexdump", "log_hexdump", "nop")

Direction = Literal["in", "out"]


def format_hexdump(data: bytes) -> str:
    """Formats the raw hex dump of the given bytes.

    Parameters:
        data: the raw bytes to format

    Returns:
        the formatted hex dump
    """
    result = []
    for line in hexdump(data, result="generator"):  # type: ignore
        _, _, line = line.partition(" ")
        result.append(line)
    return "\n".join(result)


def create_extra_args_for_logging_traffic(
    address: Any = None,
    direction: Optional[Direction] = None,
) -> dict[str, str]:
    """Creates the "extra" dict for a log entry that logs communication from
    the given address in the given direction.
    """
    extra = {}
    if direction == "in":
        extra["semantics"] = "inbound"
    elif direction == "out":
        extra["semantics"] = "outbound"

    if address:
        if not isinstance(address, str):
            address = repr(address)
        extra["id"] = address[len(address) - 10 :]

    return extra


def log_hexdump(
    log: logging.Logger,
    data: bytes,
    *,
    address: Any = None,
    direction: Optional[Direction] = None,
    level: int = logging.DEBUG,
) -> None:
    """Helper function for logging hex dumps of raw bytes, typically associated
    to some network traffic.

    Parameters:
        log: the logger to log the data to
        data: the data to log
    """
    message = format_hexdump(data)
    extra = create_extra_args_for_logging_traffic(address, direction)
    log.log(level, message, extra=extra)


def nop(*args, **kwds) -> None:
    """Function that can be called with any number of arguments and that
    does nothing.
    """
    pass

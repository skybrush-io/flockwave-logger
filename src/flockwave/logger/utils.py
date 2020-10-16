import logging

from hexdump import hexdump
from typing import Any, Optional

__all__ = ("format_hexdump", "log_hexdump")


def format_hexdump(data: bytes) -> str:
    """Formats the raw hex dump of the given bytes.

    Parameters:
        data: the raw bytes to format

    Returns:
        the formatted hex dump
    """
    result = []
    for line in hexdump(data, result="generator"):
        _, _, line = line.partition(" ")
        result.append(line)
    return "\n".join(result)


def log_hexdump(
    log: logging.Logger,
    data: bytes,
    *,
    address: Any,
    direction: Optional[str],
    level=logging.DEBUG,
) -> None:
    """Helper function for logging hex dumps of raw bytes, typically associated
    to some network traffic.

    Parameters:
        log: the logger to log the data to
        data: the data to log
    """
    message = format_hexdump(data)

    extra = {}
    if direction == "in":
        extra["semantics"] = "inbound"
    elif direction == "out":
        extra["semantics"] = "outbound"

    if address:
        if not isinstance(address, str):
            address = repr(address)
        extra["id"] = address[len(address) - 10 :]

    log.log(level, message, extra=extra)

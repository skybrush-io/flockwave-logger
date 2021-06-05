import logging

from colorlog import default_log_colors
from colorlog.colorlog import ColoredRecord
from colorlog.escape_codes import escape_codes, parse_colors
from functools import lru_cache, partial
from typing import Any, Callable, Dict, Optional

__all__ = ("styles",)


default_log_symbols = {
    "DEBUG": u" ",
    "INFO": u" ",
    "WARNING": u"\u25b2",  # BLACK UP-POINTING TRIANGLE
    "ERROR": u"\u25cf",  # BLACK CIRCLE
    "CRITICAL": u"\u25cf",  # BLACK CIRCLE
}


@lru_cache(maxsize=256)
def _get_short_name_for_logger(name: str) -> str:
    return name.rpartition(".")[2]


class ColoredFormatter(logging.Formatter):
    """Logging formatter that adds colors to the log output.

    Colors are added based on the log level and other semantic information
    stored in the log record.
    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        *,
        log_colors: Optional[Dict[str, str]] = None,
        log_symbol_colors: Optional[Dict[str, str]] = None,
        log_symbols: Optional[Dict[str, str]] = None,
        line_continuation_padding: int = 0
    ):
        """
        Constructor.

        Parameters:
            fmt: The format string to use.
            datefmt: The format string to use for dates.
            log_colors: Mapping from log level names to colors to use for the
                body text of the log message
            log_symbol_colors: Mapping from log level names to colors to use for
                the symbol of the log message
            log_symbols: Mapping from log level names to symbols
            line_continuation_padding: number of spaces to put in front of
                all but the first line in multi-line log messages
        """
        if fmt is None:
            fmt = "{log_color}{levelname}:{name}:{message}{reset}"

        super().__init__(fmt, datefmt, style="{")

        if log_colors is None:
            log_colors = default_log_colors

        self.log_colors = {k: parse_colors(v) for k, v in log_colors.items()}
        self.log_symbols = (
            log_symbols if log_symbols is not None else default_log_symbols
        )
        self.log_symbol_colors = {
            k: parse_colors(v) for k, v in log_symbol_colors.items()
        }

        if line_continuation_padding > 0:
            self._line_continuation = "\n" + (" " * line_continuation_padding)
        else:
            self._line_continuation = None

    def format(self, record: Any) -> str:
        """Format a message from a log record object."""
        if not hasattr(record, "semantics"):
            record.semantics = None
        if not hasattr(record, "id"):
            record.id = ""

        record = ColoredRecord(record)
        record.log_color = self.get_preferred_color(record, self.log_colors)
        record.log_symbol = self.get_preferred_symbol(record)
        record.log_symbol_color = (
            self.get_preferred_color(record, self.log_symbol_colors) or record.log_color
        )
        record.short_name = _get_short_name_for_logger(record.name)
        message = super().format(record)

        if not message.endswith(escape_codes["reset"]):
            message += escape_codes["reset"]

        if self._line_continuation and "\n" in record.message:
            message = message.replace("\n", self._line_continuation)

        return message

    def get_preferred_color(self, record: Any, source: Dict[str, str]) -> str:
        """Return the preferred color for the given log record from the given
        color source.
        """
        color = source.get(record.levelname, "")
        if record.levelname == "INFO":
            # For the INFO level, we may override the color with the
            # semantics of the message.
            semantic_color = source.get(record.semantics)
            if semantic_color is not None:
                color = semantic_color
        return color

    def get_preferred_symbol(self, record: Any) -> str:
        """Return the preferred color for the given log record."""
        symbol = self.log_symbols.get(record.semantics)
        if symbol is not None:
            return symbol
        else:
            return self.log_symbols.get(record.levelname, "")


class PlainFormatter(logging.Formatter):
    """Logging formatter that produces a format suitable for system journals."""

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        """
        Constructor.

        Parameters:
            fmt: The format string to use.
            datefmt: The format string to use for dates.
        """
        if fmt is None:
            fmt = "{levelname}:{name}:{id}:{message}"

        super().__init__(fmt, datefmt, style="{")

    def format(self, record: Any) -> str:
        """Format a message from a log record object."""
        if not hasattr(record, "id"):
            record.id = ""

        record.short_name = _get_short_name_for_logger(record.name)

        return super().format(record)


def create_fancy_formatter(
    show_name: bool = True, show_id: bool = True
) -> logging.Formatter:
    """Creates a colorful log formatter suitable for terminal output."""
    log_colors = dict(default_log_colors)
    log_colors.update(
        DEBUG="purple",
        INFO="reset",
        inbound="bold_blue",
        outbound="bold_green",
        request="bold_blue",
        response_success="bold_green",
        response_error="bold_red",
        notification="bold_yellow",
    )
    log_symbols = dict(default_log_symbols)
    log_symbols.update(
        inbound=u"\u25c0",  # BLACK LEFT-POINTING TRIANGLE
        outbound=u"\u25b6",  # BLACK RIGHT-POINTING TRIANGLE
        request=u"\u2190",  # LEFTWARDS ARROW
        response_success=u"\u2192",  # RIGHTWARDS ARROW
        response_error=u"\u2192",  # RIGHTWARDS ARROW
        notification=u"\u2192",  # RIGHTWARDS ARROW
        success=u"\u2714",  # CHECK MARK
        failure=u"\u2718",  # BALLOT X
    )
    log_symbol_colors = dict(log_colors)
    log_symbol_colors.update(failure="bold_red", success="bold_green")

    format_string = ["{log_symbol_color}{log_symbol}{reset} "]
    line_continuation_padding = 2

    if show_name:
        format_string.append("{fg_cyan}{short_name:<11.11}{reset} ")
        line_continuation_padding += 12
    if show_id:
        format_string.append("{fg_bold_black}{id:<10.10}{reset} ")
        line_continuation_padding += 11

    format_string.append("{log_color}{message}{reset}")

    format_string = "".join(format_string)

    return ColoredFormatter(
        format_string,
        log_colors=log_colors,
        log_symbol_colors=log_symbol_colors,
        log_symbols=log_symbols,
        line_continuation_padding=line_continuation_padding,
    )


def create_plain_formatter() -> logging.Formatter:
    """Creates a log formatter suitable for system journals."""
    return PlainFormatter("{short_name}:{id}: {message}")


def create_json_formatter() -> logging.Formatter:
    """Creates a JSON formatter suitable for archival and communication with
    external processes that can parse JSON.

    Each log message occupies one line.
    """
    from pythonjsonlogger import jsonlogger

    return jsonlogger.JsonFormatter("%(levelname)s %(name)s %(message)s")


styles: Dict[str, Callable[[], logging.Formatter]] = {
    "fancy": create_fancy_formatter,
    "colorful": partial(create_fancy_formatter, show_id=False),
    "plain": create_plain_formatter,
    "symbolic": partial(create_fancy_formatter, show_id=False, show_name=False),
    "json": create_json_formatter,
}

from __future__ import annotations

import logging as pylogging
import sys
from fnmatch import fnmatch
from pprint import pformat
from typing import Callable, List, Tuple, Union

try:
    from typing import Unpack, cast
except ImportError:
    from typing_extensions import Callable, Unpack, cast

from ...exceptions.base.pest import PestException
from ...utils.functions import set_if_none
from .. import LoggingOptions, LogLevel, SinkOptions

try:
    import loguru
    from loguru import logger as loguru_logger
    from loguru._defaults import env
except ImportError as e:  # noqa: F841
    raise PestException(
        'Failed to import loguru',
        hint=(
            'Install `loguru` to use logging configuration '
            'system: `pip install pest[loguru]`, `poetry add pest[loguru]` '
            'or just `pip install loguru` or `poetry add loguru`'
        ),
    )

FORMAT = env(
    'LOGURU_FORMAT',
    str,
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
    '<level>{level: <8}</level> | '
    '<cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
    '{exception}',
)


class _InterceptorHandler(pylogging.Handler):
    def get_exc(self, record: pylogging.LogRecord) -> Tuple[str, BaseException] | None:
        exc = record.exc_info
        if (
            exc is None
            or (exc is not None and exc[0] is None)
            or (exc is not None and exc[1] is None)
        ):
            return

        return (exc[0].__name__, exc[1])

    def emit(self, record: pylogging.LogRecord) -> None:
        """intercepts a python log (logging lib) and sends it to loguru"""
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = pylogging.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == pylogging.__file__):
            frame = frame.f_back
            depth += 1

        log = loguru_logger.bind(access=True if record.name == 'uvicorn.access' else None)

        e = self.get_exc(record)

        log.opt(
            depth=depth,
            exception=record.exc_info,
        ).log(level, f'{e[0]}: {e[1]}\n\n' if e else record.getMessage())


def no_access(record: loguru.Record) -> bool:
    return record['extra'].get('access') is None


def format_record(record: loguru.Record) -> str:
    format_string: str = cast(str, FORMAT)
    if record['extra'].get('payload') is not None:
        record['extra']['payload'] = pformat(
            record['extra']['payload'], indent=4, compact=True, width=88
        )
        format_string += '\n<level>{extra[payload]}</level>'
    return format_string + '\n'


class Loguru:
    """🐀 ⇝ loguru logging system"""

    @classmethod
    def setup(cls, **options: Unpack[LoggingOptions]) -> None:
        """🐀 ⇝ sets up `loguru`. Needs `loguru` library to be installed"""
        global FORMAT
        intercept = options.get('intercept', [])
        shush = options.get('shush', [])
        level = options.get('level', LogLevel.INFO)
        fmt = options.get('format', None)
        access_log = options.get('access_log', False)
        verbose = options.get('verbose', False)
        sinks = options.get('sinks', [])

        # if a format string is provided, we replace the default
        if type(fmt) is str:
            FORMAT = fmt

        cls.__config_standard_interception(intercept, verbose)
        cls.__configure_shush(shush)
        cls.__config_sinks(sinks, level, access_log, fmt)

    @classmethod
    def __config_standard_interception(
        cls, intercept: List[str | Tuple[str, LogLevel]], verbose: bool
    ) -> None:
        """configures interception of python loggers towards `loguru`"""
        interceptor = _InterceptorHandler()
        intercepted_loggers: List[Tuple[pylogging.Logger, int]] = []
        pylogging.basicConfig(handlers=[pylogging.NullHandler()])

        # clear handlers for all loggers in standard library
        for name in pylogging.root.manager.loggerDict:
            pylogging.getLogger(name).handlers.clear()

        if verbose:
            # if verbose, intercept all loggers and set them to DEBUG
            for name in pylogging.root.manager.loggerDict:
                logger = pylogging.getLogger(name)
                if '.' not in name:
                    logger.handlers = [interceptor]
                logger.propagate = True
                logger.setLevel(pylogging.DEBUG)
                logger.disabled = False
        else:
            for wc in intercept:
                lvl = None
                if isinstance(wc, tuple):
                    wc, lvl = wc

                # make a list of all loggers that match the wildcard
                to_intercept = [
                    (pylogging.getLogger(name), lvl or pylogging.getLogger(name).level)
                    for name in pylogging.root.manager.loggerDict
                    if fnmatch(name, wc)
                ]

                if len(to_intercept) == 0:
                    to_intercept.append((pylogging.getLogger(wc), pylogging.getLogger(wc).level))

                intercepted_loggers.extend(to_intercept)

        # intercept all loggers in the list
        for logger, lvl in intercepted_loggers:
            logger.handlers = [interceptor]
            logger.propagate = False
            logger.disabled = False
            logger.setLevel(lvl)

    @classmethod
    def __configure_shush(cls, shush: List[str]) -> None:
        """disables loggers by name"""
        for logger_name in shush:
            pylogging.getLogger(logger_name).disabled = True
            loguru_logger.disable(logger_name)

    @classmethod
    def __config_sinks(
        cls,
        sinks: List[SinkOptions],
        level: LogLevel,
        access_log: bool,
        fmt: Union[str, Callable[[loguru.Record], str], None],
    ) -> None:
        """configures loguru sinks (handlers)"""
        fmt_func = fmt if callable(fmt) else format_record

        loguru_logger.configure(handlers=[])
        loguru_logger.add(
            sys.stdout,
            colorize=True,
            diagnose=False,
            format=fmt_func,
            level=level,
            filter=lambda record: ((True if access_log else no_access(record))),
        )

        for sink in sinks:
            set_if_none(cast(dict, sink), 'format', fmt_func)
            loguru_logger.add(**sink)  # type: ignore

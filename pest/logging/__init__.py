import logging
from datetime import time, timedelta
from enum import Enum
from multiprocessing.context import BaseContext
from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    TextIO,
    Tuple,
    TypedDict,
    Union,
)

LOGGER_NAME = 'pest'

if TYPE_CHECKING:
    try:
        from loguru import (
            CompressionFunction,
            FilterDict,
            FilterFunction,
            FormatFunction,
            Message,
            PathLikeStr,
            Record,
            RetentionFunction,
            RotationFunction,
            Writable,
        )
    except ImportError:
        pass


class LogLevel(int, Enum):
    """🐀 ⇝ logging levels"""

    FATAL = 50
    ERROR = 40
    WARN = 30
    INFO = 20
    DEBUG = 10
    NONE = 0


log = logging.getLogger(LOGGER_NAME)
log.setLevel(LogLevel.DEBUG)


class SinkOptions(TypedDict, total=False):
    """🐀 ⇝ config options for loguru sinks"""

    sink: Union[
        str, 'PathLikeStr', TextIO, 'Writable', Callable[['Message'], None], logging.Handler
    ]
    level: Union[str, int]
    format: Union[str, 'FormatFunction']
    filter: Union[str, 'FilterFunction', 'FilterDict']
    colorize: bool
    serialize: bool
    backtrace: bool
    diagnose: bool
    enqueue: bool
    context: Union[str, BaseContext]
    catch: bool
    rotation: Union[str, int, time, timedelta, 'RotationFunction']
    retention: Union[str, int, timedelta, 'RetentionFunction']
    compression: Union[str, 'CompressionFunction']
    delay: bool
    watch: bool
    mode: str
    buffering: int
    encoding: str


class LoggingOptions(TypedDict, total=False):
    """🐀 ⇝ config options for loguru"""

    intercept: List[Union[str, Tuple[str, LogLevel]]]
    '''list of built-in loggers to intercept using `loguru`'''
    shush: List[str]
    '''list of built-in loggers to shush using `loguru`'''
    level: LogLevel
    '''default log level for all loggers'''
    format: Union[str, Callable[['Record'], str], None]
    '''override default log format'''
    access_log: bool
    '''whether to enable access logging'''
    verbose: bool
    '''enables all loggers'''
    sinks: List[SinkOptions]

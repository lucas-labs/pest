from typing import Union

from ..logging import LoggingOptions


def setup(
    logging: Union[LoggingOptions, None] = None,
) -> None:
    """Initializes stuff that needs to be done before the application is created"""
    __setup_logging(logging)


def __setup_logging(logging: Union[LoggingOptions, None]) -> None:
    if logging is not None:
        # loguru needs to be installed in order to be able to import this
        from ..logging.loguru import Loguru

        Loguru.setup(**logging)

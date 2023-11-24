import logging

pytest_plugins = ['tools.testing.plugin']


def pytest_configure() -> None:
    # disable all loggers
    logging.disable(logging.CRITICAL)

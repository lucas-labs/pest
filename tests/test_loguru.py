

import logging
from typing import Generator

import pytest
from loguru import logger
from pytest import LogCaptureFixture

from pest.logging import log
from pest.logging.loguru.loguru import Loguru


@pytest.fixture(scope='module', autouse=True)
def my_fixture():
    """
    enable loggers at the beginning of the test session and
    disable them at the end of the test session
    """
    logging.disable(logging.NOTSET)
    yield
    logging.disable(logging.CRITICAL)


def cap_sink(caplog: LogCaptureFixture):
    return {'sink': caplog.handler}


@pytest.fixture
def loguru_cap(caplog: LogCaptureFixture) -> Generator[LogCaptureFixture, None, None]:
    Loguru.setup(
        intercept=['pest*'],
        sinks=[{
            'sink': caplog.handler,
        }]
    )
    yield caplog
    logger.remove()


@pytest.fixture
def loguru_cap_shush(caplog: LogCaptureFixture) -> Generator[LogCaptureFixture, None, None]:
    Loguru.setup(
        shush=['pest'],
        sinks=[{
            'sink': caplog.handler,
        }]
    )
    yield caplog
    logger.remove()


def test_loguru_intercept(loguru_cap: LogCaptureFixture):
    """🐀 loguru :: intercept :: should intercept pest logger"""
    msg = 'this should be intercepted by loguru'
    log.info(msg)

    record = loguru_cap.records[0]
    assert len(loguru_cap.messages) == 1
    assert msg in loguru_cap.text

    assert record.levelno == logging.INFO


def test_loguru_shush(loguru_cap_shush: LogCaptureFixture):
    """🐀 loguru :: shush :: should intercept pest logger but shush it"""
    msg = 'this should be intercepted by loguru'
    log.info(msg)

    assert len(loguru_cap_shush.messages) == 0

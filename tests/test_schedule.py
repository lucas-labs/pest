import asyncio
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from pest import Pest, ValueProvider, module
from pest.exceptions.base.pest import PestException
from pest.metadata.meta import get_meta
from pest.schedule import ScheduleModule, cron, scheduler
from pest.schedule.decorators.types.cron_meta import SchedulerType
from pest.schedule.module.services.scheduler_explorer import get_delta, repeat_at

# region: test fixtures and utilities


class MockDateTime(datetime):
    @classmethod
    def now(cls, tz=None) -> datetime:
        return cls(2024, 1, 1, 12, 0)


@pytest.fixture
def mock_datetime():
    """fixture to mock datetime with a fixed value"""
    with patch('pest.schedule.module.services.scheduler_explorer.datetime', MockDateTime):
        yield MockDateTime


@pytest.fixture
def mock_sleep():
    """fixture to mock asyncio.sleep"""
    with patch('pest.schedule.module.services.scheduler_explorer.sleep') as mock_sleep:
        mock_sleep.return_value = None
        yield mock_sleep


@pytest.fixture
def mock_ensure_future():
    """fixture to mock asyncio.ensure_future"""
    with patch('pest.schedule.module.services.scheduler_explorer.ensure_future') as mock_ef:
        yield mock_ef


# test classes
@scheduler
class FooScheduler:
    def __init__(self) -> None:
        self.counter = 0
        self.executions: List[int] = []
        self.last_execution: datetime | None = None

    @cron('*/5 * * * *', max_repetitions=5)
    def test_task(self) -> None:
        self.counter += 1
        self.executions.append(self.counter)
        self.last_execution = datetime.now()


# endregion


def test_scheduler_decorator():
    """🐀 scheduler :: @scheduler :: should inject scheduler metadata"""
    meta: Dict[str, Any] = get_meta(FooScheduler, raise_error=False)
    assert meta is not None
    assert meta.get('meta_type') == SchedulerType.SCHEDULER


def test_cron_decorator():
    """🐀 scheduler :: @cron :: should inject cron metadata"""
    meta: Dict[str, Any] = get_meta(FooScheduler.test_task)
    assert meta is not None
    assert meta.get('meta_type') == SchedulerType.CRON
    assert meta.get('cron_time') == '*/5 * * * *'


def test_get_delta_calculation(mock_datetime):
    """🐀 scheduler :: get_delta :: should calculate delta time to a cron pattern"""

    # for */5 * * * *, if current time is 12:00, next execution should be at 12:05
    delta = get_delta('*/5 * * * *')
    assert delta == 300  # 5 minutes in seconds

    # for specific time, test exact calculation
    delta = get_delta('0 15 * * *')  # 3 PM every day
    assert delta == 10800  # 3 hours in seconds


def test_invalid_cron_expression():
    """🐀 scheduler :: get_delta :: should raise ValueError for invalid cron expression"""
    with pytest.raises(ValueError) as exc_info:
        get_delta('invalid cron')
    assert 'Exactly 5, 6 or 7 columns has to be specified for iterator expression.' in str(
        exc_info.value
    )


@pytest.mark.asyncio
async def test_scheduler_execution_flow(mock_sleep, mock_ensure_future):
    """🐀 scheduler :: @scheduler :: should execute the scheduled job as expected"""

    def side_effect(coro: Any) -> asyncio.Task:
        return asyncio.create_task(coro)

    mock_ensure_future.side_effect = side_effect

    @module(
        imports=[ScheduleModule],
        providers=[ValueProvider(provide=FooScheduler, use_value=FooScheduler())],
    )
    class TestModule:
        pass

    app = Pest.create(TestModule)

    with TestClient(app):
        scheduler_instance = app.resolve(FooScheduler)

        # let the event loop process the scheduled task; wait longer so all scheduled runs occur
        await asyncio.sleep(0.1)  # increased sleep duration

        # verify the mocks were called correctly
        assert mock_ensure_future.called
        assert mock_sleep.called

        # verify the task was executed 5 times
        assert scheduler_instance.counter == 5
        assert len(scheduler_instance.executions) == 5


@pytest.mark.asyncio
async def test_repeat_at_decorator(mock_sleep):
    """🐀 scheduler :: @repeat_at :: should execute the scheduled job as expected"""
    counter = 0

    @repeat_at(cron='*/5 * * * *', max_repetitions=1)
    async def test_job() -> None:
        nonlocal counter
        counter += 1

    # execute the wrapped function
    test_job()
    await asyncio.sleep(0)  # let the event loop process the task

    # verify sleep was called with correct time
    assert mock_sleep.called


def test_schedule_module_required_dependencies():
    """🐀 scheduler :: ScheduleModule :: should raise PestException if croniter is not installed"""
    with patch.dict('sys.modules', {'croniter': None}):
        with pytest.raises(PestException) as exc_info:
            import importlib

            import pest.schedule.module.services.scheduler_explorer as scheduler_module

            importlib.reload(scheduler_module)

        assert 'Failed to import croniter' in str(exc_info.value)

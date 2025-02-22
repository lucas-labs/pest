from asyncio import ensure_future, iscoroutinefunction, sleep
from datetime import datetime
from functools import wraps
from inspect import getmembers, isfunction
from typing import Any, Callable, Coroutine, List, Optional, Tuple

from fastapi.concurrency import run_in_threadpool

from pest.core.application import PestApplication

from ....core.common import OnApplicationBootstrap
from ....exceptions.base.pest import PestException
from ....logging import log
from ....metadata.meta import get_meta, get_meta_value
from ....metadata.types._meta import PestType
from ...decorators.types.cron_meta import CronMeta, SchedulerMeta, SchedulerType

try:
    from croniter import croniter
except ImportError:
    raise PestException(
        'Failed to import croniter',
        hint=(
            'Install `croniter` to use task scheduling functionality: '
            '`pip install pest-py[cron]`, `poetry add pest-py[cron]` '
            'or just `pip install croniter` or `poetry add croniter`'
        ),
    )


def jobs_in(cls: Any) -> List[Tuple[Callable, CronMeta]]:
    members = getmembers(cls, lambda m: isfunction(m))
    handlers: List[Tuple[Callable, CronMeta]] = []

    for _, method in members:
        meta_type = get_meta_value(method, key='meta_type', type=PestType, default=None)
        if meta_type == SchedulerType.CRON:
            handlers.append((method, get_meta(method, CronMeta)))

    return handlers


def get_delta(cron: str) -> float:
    """
    This function returns the time delta between now and the next cron execution time.
    """
    now = datetime.now()
    crontime = croniter(cron, now)
    return (crontime.get_next(datetime) - now).total_seconds()


def repeat_at(
    *,
    cron: str,
    max_repetitions: Optional[int] = None,
    raise_exceptions: bool = False,
) -> Any:
    """
    This function returns a decorator that makes a function execute periodically as per the cron
    expression provided.

    ### Params
    - cron: cron-style string for periodic execution, eg. '0 0 * * *' every midnight
    - max_repetitions: Maximum number of times the function should be executed.
      If `None`, it will run indefinitely. Default is `None`.
    - raise_exceptions: whether to raise exceptions or not. Default is `False`.
    """

    def decorator(func: Callable) -> Any:
        """transform the function into a periodic scheduled job"""
        is_coroutine = iscoroutinefunction(func)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            repititions = 0
            if not croniter.is_valid(cron):
                raise ValueError(f"Invalid cron expression: '{cron}'")

            async def loop(*args: Any, **kwargs: Any) -> None:
                nonlocal repititions
                while max_repetitions is None or repititions < max_repetitions:
                    try:
                        sleepTime = get_delta(cron)
                        await sleep(sleepTime)
                        if is_coroutine:
                            await func(*args, **kwargs)
                        else:
                            await run_in_threadpool(func, *args, **kwargs)
                        await sleep(0.5)  # sleep for 0.5 seconds to avoid multiple executions
                    except Exception as e:
                        if log is not None:
                            log.exception(e)
                        if raise_exceptions:
                            raise e
                    repititions += 1

            ensure_future(loop(*args, **kwargs))

        return wrapper

    return decorator


class SchedulerExplorer(OnApplicationBootstrap):
    async def on_application_bootstrap(
        self, app: PestApplication
    ) -> Optional[Coroutine[Any, Any, None]]:
        for token in app.provides():
            # check if it's a scheduler
            sched_meta = get_meta(token, raise_error=False, output_type=SchedulerMeta)
            if (
                sched_meta is not None
                and getattr(sched_meta, 'meta_type', None) == SchedulerType.SCHEDULER
            ):
                # we found a scheduler, now let's loop over its methods to find
                # which ones has a CronMeta
                scheduler = app.resolve(token)

                for job, cron_meta in jobs_in(token):
                    repeateable = repeat_at(
                        cron=cron_meta.cron_time, max_repetitions=cron_meta.max_repetitions
                    )(job)
                    # calls the decorator to repeat the function at the specified time
                    repeateable(scheduler)

        return super().on_application_bootstrap(app)

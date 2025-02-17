from typing import Callable, TypeVar

from dacite import Config, from_dict

from ...metadata.meta import inject_metadata
from .types.cron_meta import CronMeta, SchedulerMeta
from .types.dicts.cron_dict import CronMetaDict

try:
    from typing import Unpack
except ImportError:
    from typing_extensions import Unpack

from fastapi.types import DecoratedCallable

from pest.decorators._common import meta_decorator


def cron(
    cron_time: str, **options: Unpack[CronMetaDict]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ mark the method as a cron job"""
    return meta_decorator(
        meta_type=CronMeta,
        meta={
            'cron_time': cron_time,
            **options,
        },
    )


T = TypeVar('T')
K = TypeVar('K')


def scheduler(cls: type[T]) -> type[T]:
    """🐀 ⇝ mark the service as a job scheduler"""
    inject_metadata(
        cls,
        from_dict(
            SchedulerMeta,
            {},
            config=Config(check_types=False),
        ),
    )
    return cls

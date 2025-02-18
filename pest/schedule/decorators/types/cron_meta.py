from dataclasses import dataclass, field
from enum import Enum
from typing import Union

from ....metadata.types._meta import Meta


class SchedulerType(str, Enum):
    CRON = 'CRON'
    SCHEDULER = 'SCHEDULER'


@dataclass
class ScheduleMeta(Meta):
    meta_type: SchedulerType
    '''🐀 ⇝ type of the metadata'''


@dataclass
class CronMeta(ScheduleMeta):
    meta_type: SchedulerType = field(
        default=SchedulerType.CRON, init=False, metadata={'expose': False}
    )
    cron_time: str = field(metadata={'expose': False})
    '''🐀 ⇝ cron time string'''
    max_repetitions: Union[int, None] = field(default=None)
    '''🐀 ⇝ maximum number of repetitions'''
    name: Union[str, None] = field(default=None)
    '''🐀 ⇝ name of the cron job'''


@dataclass
class SchedulerMeta(ScheduleMeta):
    meta_type: SchedulerType = field(
        default=SchedulerType.SCHEDULER, init=False, metadata={'expose': False}
    )

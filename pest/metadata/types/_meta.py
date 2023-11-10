from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class MetaType(str, Enum):
    MODULE = 'MODULE'
    INJECTABLE = 'INJECTABLE'
    CONTROLLER = 'CONTROLLER'
    HANDLER = 'HANDLER'


@dataclass
class Meta(Protocol):
    meta_type: MetaType

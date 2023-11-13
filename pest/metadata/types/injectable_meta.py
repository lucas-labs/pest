from dataclasses import dataclass, field

from ._meta import Meta, PestType


@dataclass
class InjectableMeta(Meta):
    meta_type: PestType = field(default=PestType.INJECTABLE, init=False)

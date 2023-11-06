from dataclasses import dataclass, field

from ._meta import Meta, MetaType


@dataclass
class InjectableMeta(Meta):
    meta_type: MetaType = field(default=MetaType.INJECTABLE, init=False)

from typing import Sequence, TypeAlias

from starlette.middleware import Middleware as StarletteMiddleware

from .base import PestMwDispatcher

MiddlewareDef: TypeAlias = Sequence[StarletteMiddleware | PestMwDispatcher]

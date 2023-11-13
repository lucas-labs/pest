
from inspect import getmembers, isfunction
from typing import TYPE_CHECKING, Any, ClassVar, Optional

from fastapi.routing import APIRoute

from ..metadata.meta import get_meta, get_meta_value
from ..metadata.types._meta import PestType
from ..metadata.types.handler_meta import HandlerMeta
from ..utils.fastapi.router import PestRouter
from .common import PestPrimitive
from .handler import HandlerTuple, setup_handler
from .types.status import Status

if TYPE_CHECKING:
    from .module import Module

NOT_CONTROLLER = 'Class {cls} is not a subclass of Controller'


def setup_controller(cls: type, module: Optional['Module'] = None) -> None:
    """🐀 ⇝ sets up a `controller` class"""
    if not issubclass(cls, Controller):
        raise TypeError(NOT_CONTROLLER.format(cls=cls.__name__))
    cls.__setup_controller_class__(module)


def router_of(cls: type) -> PestRouter:
    """🐀 ⇝ obtains a `controller`'s router"""
    if not issubclass(cls, Controller):
        raise TypeError(NOT_CONTROLLER.format(cls=cls.__name__))

    if cls.__router__ is None:
        raise ValueError(f'Controller {cls.__name__} has not been setup')

    return cls.__router__


def routes_of(cls: type) -> list[APIRoute]:
    """🐀 ⇝ obtains all routes of a `controller`"""
    return router_of(cls).routes


def module_of(cls: type) -> 'Module':
    if not issubclass(cls, Controller):
        raise TypeError(NOT_CONTROLLER.format(cls=cls.__name__))

    mod = cls.__parent_module__
    if mod is None:
        raise ValueError(f'Parent module of controller {cls.__name__} has not been setup')

    return mod


class Controller(PestPrimitive):
    __router__: ClassVar[PestRouter]
    __parent_module__: ClassVar[Optional[Any]]

    @classmethod
    @property
    def __pest_object_type__(cls) -> PestType:
        return PestType.CONTROLLER

    @classmethod
    def __setup_controller_class__(cls, module: Optional['Module']) -> None:
        """sets up a controller class"""
        meta = get_meta(cls, type=dict)
        cls.__router__ = PestRouter(
            prefix=meta['prefix'],
        )
        cls.__parent_module__ = module

        router = cls.__make_router__()
        cls.__router__.include_router(router)
        cls.__class_status__ = Status.READY

    @classmethod
    def __make_router__(cls) -> PestRouter:
        """sets up a controller's router"""
        r = PestRouter()

        for route in cls.__routes__():
            r.routes.append(route)

        return r

    @classmethod
    def __routes__(cls, ) -> list[APIRoute]:
        """makes routes for the controller"""

        routes = []
        for handler in cls.__handlers__():
            ruote = setup_handler(cls, handler)
            routes.append(ruote)
        return routes

    @classmethod
    def __handlers__(cls) -> list[HandlerTuple]:
        members = getmembers(cls, lambda m: isfunction(m))
        handlers: list[HandlerTuple] = []

        for _, method in members:
            meta_type = get_meta_value(method, key='meta_type', type=PestType, default=None)
            if meta_type == PestType.HANDLER:
                handlers.append((method, get_meta(method, type=HandlerMeta)))

        return handlers

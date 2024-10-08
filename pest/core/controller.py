from inspect import getmembers, isfunction
from typing import TYPE_CHECKING, Any, ClassVar, List, Optional

from fastapi.routing import APIRoute

from ..exceptions.base.pest import PestException
from ..metadata.meta import get_meta, get_meta_value, inject_metadata
from ..metadata.types._meta import PestType
from ..metadata.types.controller_meta import ControllerMeta
from ..metadata.types.handler_meta import HandlerMeta
from ..utils.fastapi.router import PestRouter
from ..utils.functions import classproperty
from .common import PestPrimitive
from .handler import HandlerTuple, setup_handler
from .types.status import Status

if TYPE_CHECKING:  # pragma: no cover
    from .module import Module

NOT_CONTROLLER = 'Class {cls} is not a subclass of Controller'
NOT_ROUTER = 'Object is not a subclass of PestRouter'


def setup_controller(cls: type, module: Optional['Module'] = None) -> None:
    """🐀 ⇝ sets up a `controller` class"""
    if not issubclass(cls, Controller):
        raise PestException(NOT_CONTROLLER.format(cls=cls.__name__))
    cls.__setup_controller_class__(module)


def router_of(cls: type) -> PestRouter:
    """🐀 ⇝ obtains a `controller`'s router"""
    if not issubclass(cls, Controller):
        raise PestException(NOT_CONTROLLER.format(cls=cls.__name__))

    if cls.__router__ is None:
        raise PestException(f'Controller {cls.__name__} has not been setup')

    return cls.__router__


def routes_of(cls: type) -> List[APIRoute]:
    """🐀 ⇝ obtains all routes of a `controller`"""
    return router_of(cls).routes


def module_of(cls: type) -> 'Module':
    """🐀 ⇝ obtains the parent module of a `controller`"""
    if not issubclass(cls, Controller):
        raise PestException(NOT_CONTROLLER.format(cls=cls.__name__))

    mod = cls.__parent_module__
    if mod is None:
        raise PestException(f'Parent module of controller {cls.__name__} has not been setup')

    return mod


class Controller(PestPrimitive):
    __router__: ClassVar[PestRouter]
    __parent_module__: ClassVar[Optional[Any]]

    @classproperty
    def __pest_object_type__(cls) -> PestType:
        return PestType.CONTROLLER

    @classmethod
    def __str__(cls) -> str:
        meta = get_meta(cls, ControllerMeta, clean=True)
        return f'Controller {meta.prefix}'

    @classmethod
    def __setup_controller_class__(cls, module: Optional['Module']) -> None:
        """sets up a controller class"""
        meta = get_meta(cls, dict, clean=True)
        cls.__router__ = PestRouter(**meta)
        cls.__parent_module__ = module
        inject_metadata(cls.__router__, name=f'{cls.__name__} {meta.get("prefix", "")}')

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
    def __routes__(cls) -> List[APIRoute]:
        """makes routes for the controller"""

        routes = []
        for handler in cls.__handlers__():
            ruote = setup_handler(cls, handler)
            routes.append(ruote)
        return routes

    @classmethod
    def __handlers__(cls) -> List[HandlerTuple]:
        members = getmembers(cls, lambda m: isfunction(m))
        handlers: List[HandlerTuple] = []

        for _, method in members:
            meta_type = get_meta_value(method, key='meta_type', type=PestType, default=None)
            if meta_type == PestType.HANDLER:
                handlers.append((method, get_meta(method, HandlerMeta)))

        return handlers

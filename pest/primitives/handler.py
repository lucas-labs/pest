
from dataclasses import asdict
from inspect import Parameter, signature
from typing import TYPE_CHECKING, Any, Callable, TypeAlias

from fastapi import Depends, Request
from fastapi.routing import APIRoute

from ..metadata.types.handler_meta import HandlerMeta
from ..utils.functions import clean_dict

if TYPE_CHECKING:  # pragma: no cover
    from .controller import Controller

HandlerFn: TypeAlias = Callable[..., Any]
HandlerTuple: TypeAlias = tuple[HandlerFn, HandlerMeta]


def setup_handler(cls: type['Controller'], handler: HandlerTuple) -> APIRoute:
    """🐀 ⇝ sets up a request handler"""
    from ..decorators.dicts.handler_dict import HandlerMetaDict
    handler_fn, handler_meta = handler
    meta_dict = clean_dict(asdict(handler_meta), HandlerMetaDict)
    route = APIRoute(
        endpoint=handler_fn,
        path=handler_meta.path,
        methods=handler_meta.methods,
        **meta_dict
    )
    _patch_route_signature(cls, route)

    return route


def _patch_route_signature(cls: type['Controller'], route: APIRoute) -> None:
    """
    changes the signature of a route's endpoint to ensure that FastAPI
    performs dependency injection correctly and does not expect a `self`
    parameter as a query parameter.
    """
    controller = PestControllerInjector(token=cls)

    old_endpoint = route.endpoint
    old_signature = signature(old_endpoint)
    old_parameters: list[Parameter] = list(old_signature.parameters.values())
    old_first_parameter = old_parameters[0]
    new_first_parameter = old_first_parameter.replace(default=Depends(controller))
    new_parameters = [new_first_parameter] + [
        parameter.replace(kind=Parameter.KEYWORD_ONLY) for parameter in old_parameters[1:]
    ]
    new_signature = old_signature.replace(parameters=new_parameters)
    setattr(route.endpoint, '__signature__', new_signature)


class PestControllerInjector:
    """🐀 ⇝ injector to be used with fastapi's `Depends`"""

    def __init__(
        self,
        token: type['Controller'],
    ):
        """🐀 ⇝ initializes a new injector

        Args:
            token (InjectionToken): the token to be injected
        """
        self.token = token

    async def __call__(self, request: Request) -> Any:
        """🐀 ⇝ returns the controller to be injected"""
        from .controller import module_of
        module = module_of(self.token)
        controller = module.get(self.token)

        return controller

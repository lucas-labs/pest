from dataclasses import asdict
from inspect import Parameter, isclass, isfunction, signature
from typing import TYPE_CHECKING, Any, Callable, List, Tuple, Type, Union, get_args

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

from fastapi import Depends, Request
from fastapi.routing import APIRoute

from pest.di.injection import _Inject, inject

from ..exceptions.base.pest import PestException
from ..metadata.types.handler_meta import HandlerMeta
from ..middleware.di import scope_from
from ..utils.functions import clean_dict

if TYPE_CHECKING:  # pragma: no cover
    from ..metadata.types.module_meta import InjectionToken
    from .controller import Controller

HandlerFn: TypeAlias = Callable[..., Any]
HandlerTuple: TypeAlias = Tuple[HandlerFn, HandlerMeta]


def setup_handler(cls: Type['Controller'], handler: HandlerTuple) -> APIRoute:
    """
    Sets up a request handler.

    @internal
    """
    from ..decorators.dicts.handler_dict import HandlerMetaDict

    handler_fn, handler_meta = handler
    meta_dict = clean_dict(asdict(handler_meta), HandlerMetaDict)
    _patch_handler_fn(cls, handler_fn)

    route = APIRoute(
        endpoint=handler_fn,
        path=handler_meta.path,
        methods=handler_meta.methods,
        **meta_dict,
    )

    return route


def _patch_handler_fn(cls: Type['Controller'], handler: HandlerFn) -> None:
    """
    Changes the signature of a route's endpoint to ensure that FastAPI
    performs dependency injection correctly and doesn't expect a `self`
    parameter as a query parameter. To do so, we replace the first
    parameter of the endpoint with a `Depends` object that resolves the
    controller instance using `rodi`.

    It also replaces any parameter annotated with `inject` or with a
    default value of `_Inject` with a `Depends` object that resolves the
    value using the `module`'s rodi container. This last step is
    performed by `PestFastAPIInjector`.

    @internal
    """

    controller = PestFastAPIInjector(token=cls, controller=cls)

    old_endpoint = handler
    old_signature = signature(old_endpoint)
    old_parameters: List[Parameter] = list(old_signature.parameters.values())
    old_first_parameter = old_parameters[0]
    new_first_parameter = old_first_parameter.replace(default=Depends(controller))
    new_parameters = [_get_new_param(cls, parameter) for parameter in old_parameters[1:]]
    new_signature = old_signature.replace(parameters=[new_first_parameter] + new_parameters)

    setattr(handler, '__signature__', new_signature)


def _get_new_param(ctrl: type, parameter: Parameter) -> Parameter:
    """
    If the parameter is expected to be injected by `pest` (either by annotating it with `inject` or
    by having a default value of `_Inject` returned by `= inject(something)`), we replace it with a
    FastAPI's `Depends` that resolves the value using the `module`'s rodi container. This last step
    is performed by `PestFastAPIInjector`.

    @internal
    """
    if parameter.annotation is not Parameter.empty or isinstance(parameter.default, _Inject):
        pest_anns = _get_pest_injection(parameter)
        if pest_anns is not None:
            # it has a pest injection annotation

            if len(pest_anns) > 1:
                raise PestException(
                    'Multiple injection annotations are not allowed!',
                    hint=f'Parameter {parameter.name} has {len(pest_anns)} injection annotation!',
                )

            annotation = pest_anns[0]
            if annotation.token is not None:
                # if the token is a function, we replace it with a FastAPI's `Depends(dep)` call
                if isfunction(annotation.token):
                    parameter = parameter.replace(default=Depends(annotation.token))
                elif isclass(annotation.token):
                    # otherwise we replace the parameter with a `Depends` on `PestFastAPIInjector`
                    # which will try to resolve the value from the `module`'s container
                    parameter = parameter.replace(
                        default=Depends(
                            PestFastAPIInjector(controller=ctrl, token=annotation.token)
                        )
                    )
                else:
                    raise PestException(
                        'Invalid injection annotation token!',
                        hint=f'Parameter {parameter.name} has an invalid injection token!',
                    )
    return parameter.replace(kind=Parameter.KEYWORD_ONLY)


def _get_pest_injection(parameter: Parameter) -> Union[List[_Inject], None]:
    """
    checks if the parameter is annotated with `inject` or has a default value of `_Inject`.
    If so, it returns a list of `_Inject` annotations, otherwise it returns `None`.

    @internal
    """

    if isinstance(parameter.default, _Inject):
        token = (
            parameter.default.token
            if parameter.default.token is not None
            else parameter.annotation
            if parameter.annotation is not Parameter.empty
            else None
        )
        annotations = (token, inject)
    else:
        annotations = get_args(parameter.annotation)

    if len(annotations) == 0:
        return None

    token, anns = annotations[0], annotations[1:]

    if token is None:
        raise PestException(
            'Missing injection annotation token!',
            hint=f'Parameter {parameter.name} has no injection annotation!',
        )

    anns = [
        annotation if isinstance(annotation, _Inject) else _Inject(token)
        for annotation in anns
        if isinstance(annotation, _Inject) or annotation is inject
    ]

    for annotation in anns:
        if annotation.token is None:
            annotation.token = token

    return anns if len(anns) > 0 else None


class PestFastAPIInjector:
    """
    Injector to be used with fastapi's `Depends`

    This injector is used to bypass the `Depends` mechanism of FastAPI
    and inject stuff into the handler's signature ourselves using
    the `module`'s container.

    @internal
    """

    def __init__(self, controller: Type['Controller'], token: 'InjectionToken'):
        self.controller = controller
        self.token = token

    async def __call__(self, request: Request) -> Any:
        """🐀 ⇝ returns the `controller` to be injected 💉"""
        from .controller import module_of

        scope = scope_from(request)
        module = module_of(self.controller)
        di_result = await module.aget(self.token, scope)

        return di_result

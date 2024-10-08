from inspect import Signature, isclass, isfunction
from typing import (
    Any,
    Callable,
    Optional,
    Protocol,
    Tuple,
    Type,
    Union,
    cast,
    final,
    runtime_checkable,
)

try:
    from typing import TypeAlias, TypeGuard
except ImportError:
    from typing_extensions import TypeAlias, TypeGuard

from dij import ActivationScope
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, T
from starlette.middleware.base import RequestResponseEndpoint as CallNext
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from ..core.module import Module
from ..metadata.types.module_meta import InjectionToken
from .di import scope_from

ProvideFn: TypeAlias = Callable[[InjectionToken[T], Optional[ActivationScope]], T]
UseFn: TypeAlias = Callable[[Request, CallNext], Response]


@runtime_checkable
class PestMiddlwareCallback(Protocol):
    async def __call__(
        self,
        request: Request,
        call_next: CallNext,
    ) -> Response: ...


@runtime_checkable
class PestMiddleware(Protocol):
    async def use(self, request: Request, call_next: CallNext) -> Response: ...

    @final
    async def __call__(
        self,
        request: Request,
        call_next: CallNext,
    ) -> Response:
        return await self.use(request, call_next)


class PestBaseHTTPMiddleware(BaseHTTPMiddleware):
    """🐀 ⇝ asgi middleware that receivs an injetor function and a dispatch funtion

    same as `starlette`'s `BaseHTTPMiddleware` but this one supports di injection
    """

    def __init__(
        self, app: ASGIApp, parent_module: Module, dispatch: PestMiddlwareCallback
    ) -> None:
        self.parent_module = parent_module
        super().__init__(app, dispatch=self.__dispatch_fn(dispatch))

    def __dispatch_fn(
        self, dispatch: Union[PestMiddlwareCallback, Type[PestMiddlwareCallback]]
    ) -> Union[DispatchFunction, None]:
        if dispatch is None:
            return dispatch

        if _is_class_pest_mw_callback(dispatch):
            self.parent_module.register(dispatch)

        async def wrapper(request: Request, call_next: CallNext) -> Response:
            scope = scope_from(request)
            dispatch_fn = cast(
                PestMiddlwareCallback,
                (
                    dispatch
                    if not isclass(dispatch)
                    else self.parent_module.get(dispatch, scope, fail_on_coroutine=False)
                ),
            )

            args, kwargs = await self.__resolve_dispatcher_args(dispatch_fn, scope)
            return await dispatch_fn(request, call_next, *args, **kwargs)

        return wrapper

    async def __resolve_dispatcher_args(
        self, function: DispatchFunction, scope: Union[ActivationScope, None]
    ) -> Tuple[tuple, dict]:
        signature = Signature.from_callable(function)
        parameters = signature.parameters
        args = []
        kwargs = {}

        arg_count = 0
        for name, param in parameters.items():
            if arg_count < 2:
                arg_count += 1
                continue

            if param.kind == param.POSITIONAL_ONLY or param.kind == param.POSITIONAL_OR_KEYWORD:
                args.append(await self.parent_module.aget(param.annotation, scope))

            elif param.kind == param.KEYWORD_ONLY:
                kwargs[name] = await self.parent_module.aget(param.annotation, scope)

        return tuple(args), kwargs


def _is_class_pest_mw_callback(obj: Any) -> TypeGuard[Type[PestMiddlwareCallback]]:
    """checks if an object is a **class** that respects the pest middleware callback protocol"""
    return _is_pest_mw_callback(obj) and isclass(obj)


def _is_pest_mw_callback(
    obj: Any,
) -> TypeGuard[Union[PestMiddlwareCallback, Type[PestMiddlwareCallback]]]:
    """checks if an object respects the pest middleware callback protocol"""
    respects_protocol = (
        isclass(obj)
        and issubclass(obj, PestMiddlwareCallback)
        or callable(obj)
        and isinstance(obj, PestMiddlwareCallback)
    )

    if not respects_protocol:
        return False

    # Check the function signature
    is_function = isfunction(obj)
    fn = obj if is_function else obj.__call__
    params = Signature.from_callable(fn).parameters
    args = list(params) if is_function else list(params)[1:]

    # Check if the first two arguments are 'request' and 'call_next'
    if args[:2] != ['request', 'call_next']:
        return False

    return True

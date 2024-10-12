import inspect
from functools import wraps
from inspect import Parameter, getmembers, iscoroutinefunction, isfunction, signature
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    Union,
    get_args,
)

from fastapi import Depends, Request

from ..core.handler import HandlerFn
from ..exceptions.http.http import ForbiddenException
from ..metadata.meta import get_meta, get_meta_value
from ..metadata.types._meta import PestType

GuardCb = Callable[[Dict[str, Any]], None]


# TODO: Guard config
#       Similar to how **pydantic's config** works, we could have an optional `GuardConfig` class
#       that could be used to configure the behavior of the guard.
#       This will allow us to get rid of the `**depends` parameter in the `use_guard` decorator
#       and make it a guard class-level configuration instead. Or maybe we could have both
#       (per-route and per-guard config). To do so, we would have to make Guard an `ABC` instead of
#       a `Protocol` and add a `config` attribute to it.


class GuardCtx(Dict[str, Any]):
    def dep(self, key: str) -> Any:
        deps = self.deps()
        return deps.get(key, None)

    def deps(self) -> Dict[str, Any]:
        return self.get('__pest_guard_deps__', {})


class Guard(Protocol):
    """🐀 ⇝ base guard protocol"""

    def can_activate(
        self, request: Request, *, context: GuardCtx, set_result: GuardCb
    ) -> Union[bool, Awaitable[bool]]:
        """🐀 ⇝ determines if the request can be activated by the current request"""
        ...


def use_guard(guard: Type[Guard], **depends: Any) -> Callable:
    """🐀 ⇝ decorator to apply a guard either to a single method or all methods in a class"""

    def decorator(target: Callable) -> Callable:
        if isinstance(target, type):  # If it's a class, apply to all methods
            return _apply_guard_to_class(target, guard, depends)
        else:
            return _apply_guard_to_method(target, guard, depends)

    return decorator


class GuardExtra(Dict[str, Any]):
    pass


def _extract_params(params: List[Parameter]) -> Tuple[Optional[Parameter], List[Parameter]]:
    """
    extracts the request and all parameters annotated with "guard_extra" from a list of parameters
    """
    request_param = None
    extra_params = []

    for param in params:
        if param.annotation == Request:
            request_param = param
        elif param.annotation is GuardExtra:
            extra_params.append(param)
        else:
            anns = get_args(param.annotation)
            if len(anns) == 0:
                continue

            typing, metas = anns[0], anns[1:]
            if typing == GuardExtra or GuardExtra in metas:
                extra_params.append(param)

    return request_param, extra_params


# applies the guard to a single method
def _apply_guard_to_method(
    func: Callable, guard: Type[Guard], depends: Dict[str, Any] = {}
) -> Callable:
    sig = signature(func)
    params: List[Parameter] = list(sig.parameters.values())

    # check if there's any parameter annotated with type Request
    request_parameter, extras = _extract_params(params)
    request_was_in_original_sig = request_parameter is not None

    if request_parameter is None:
        # add the parameter to the signature, annotated with type Request
        request_param_name = '__pest_guard_request__'
        params = [
            *params,
            Parameter(request_param_name, Parameter.POSITIONAL_OR_KEYWORD, annotation=Request),
        ]
    else:
        request_param_name = request_parameter.name

    # add dependencies to the route parameters
    for key, value in depends.items():
        params = [
            *params,
            Parameter(f'__pest_guard_dep_{key}__', Parameter.KEYWORD_ONLY, default=Depends(value)),
        ]

    # remove the extras the `params` list
    params = [param for param in params if param not in extras]

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        meta = get_meta(func)

        # try to extract the request object from kwargs or args
        request = kwargs.get(request_param_name)
        if request is None:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if not request:
            raise ValueError('Request object not found in args or kwargs')

        extra_result: Dict[str, Any] = {}

        def set_result(result: Dict[str, Any]) -> None:
            nonlocal extra_result
            extra_result = result

        # get the deps from the kwargs and add them to the meta, into a __pest_guard_deps__ dict
        deps = {key: kwargs.pop(f'__pest_guard_dep_{key}__', None) for key in depends.keys()}
        meta['__pest_guard_deps__'] = deps

        # apply the guard
        guard_instance = guard()
        verdict = guard_instance.can_activate(
            request, context=GuardCtx(meta), set_result=set_result
        )
        if inspect.isawaitable(verdict):
            verdict = await verdict

        if verdict is False:
            raise ForbiddenException('Not authorized')

        # if the request was not in the original signature, remove it from args/kwargs
        if not request_was_in_original_sig:
            kwargs.pop(request_param_name, None)
            args = tuple([arg for arg in args if not isinstance(arg, Request)])

        # add the extra result to the signature
        for param in extras:
            if param.annotation is GuardExtra:
                kwargs[param.name] = extra_result
            else:
                kwargs[param.name] = extra_result.get(param.name, None)

        return await func(*args, **kwargs) if iscoroutinefunction(func) else func(*args, **kwargs)

    # update the signature to include the new 'request' parameter
    setattr(wrapper, '__signature__', sig.replace(parameters=params))
    return wrapper


# applies the guard to all methods in a class
def _apply_guard_to_class(cls: type, guard: Type[Guard], depends: Dict[str, Any] = {}) -> type:
    members = getmembers(cls, lambda m: isfunction(m))
    handlers: List[HandlerFn] = []

    for _, method in members:
        meta_type = get_meta_value(method, key='meta_type', type=PestType, default=None)
        if meta_type == PestType.HANDLER:
            handlers.append(method)

    for handler in handlers:
        replacement = _apply_guard_to_method(handler, guard, depends)
        setattr(cls, handler.__name__, replacement)

    return cls

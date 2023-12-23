from typing import Tuple, Union

from .colorize import c


def as_tree(
    obj: Union[object, Tuple[str, str]],
    prefix: str = '',
    is_last: bool = True,
    with_providers: bool = True,
    with_controllers: bool = True,
) -> str:
    """returns a tree representation of the module and its submodules"""
    if isinstance(obj, tuple):
        t, n = obj
        if t == 'provider':
            obj_name = '│' + c(f'{" ○ " if prefix else ""}{n}', color='magenta')
        else:
            obj_name = '│' + c(f'{" □ " if prefix else ""}{n}', color='blue')
    else:
        obj_name = f'{"├─ " if prefix else ""}{obj.__class__.__name__}'

    result = ''

    if prefix:
        result += prefix + obj_name + '\n'
    else:
        result += f'{c(obj_name, color="green", attrs=["underline"])} 🐀' + '\n' + '    │\n'

    prefix += '│   ' if not is_last else '    '

    if with_providers:
        providers = getattr(obj, 'providers', [])
        for i, provider in enumerate(providers):
            provider_name = _get_provider_name(provider)
            result += as_tree(('provider', provider_name), prefix, i == len(providers) - 1)

    if with_controllers:
        controllers = getattr(obj, 'controllers', [])
        for i, controller in enumerate(controllers):
            controller_name = controller.__name__
            result += as_tree(('controller', controller_name), prefix, i == len(controllers) - 1)

    imports = getattr(obj, 'imports', [])
    for i, sub_module in enumerate(imports):
        result += as_tree(sub_module, prefix, i == len(imports) - 1)

    return result


def _get_provider_name(provider: type) -> str:
    injection_token = getattr(provider, 'provide', None)

    if injection_token is None:
        return provider.__name__

    if isinstance(injection_token, str):
        return injection_token

    return injection_token.__name__

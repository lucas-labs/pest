from .decorators.controller import api, controller, ctrl, router, rtr
from .decorators.handler import delete, get, head, options, patch, post, put, trace
from .decorators.module import dom, domain, mod, module
from .factory import Pest

__all__ = [
    'Pest',
    # decorators - module
    'module',
    'mod',
    'domain',
    'dom',
    # decorators - handler
    'get',
    'post',
    'put',
    'delete',
    'patch',
    'options',
    'head',
    'trace',
    # decorators - controller
    'controller',
    'ctrl',
    'router',
    'rtr',
    'api',
]

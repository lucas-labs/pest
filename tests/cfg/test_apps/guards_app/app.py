import json
from base64 import b64decode
from dataclasses import dataclass
from typing import Any, Callable

from fastapi import Request

from pest import Guard, GuardCb, GuardExtra, Pest, controller, get, meta, module, use_guard
from pest.core.application import PestApplication
from pest.exceptions.http.http import UnauthorizedException

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


@dataclass
class User:
    id: int
    name: str
    role: str


class AuthGuard(Guard):
    def can_activate(self, request: Request, *, context: Any, set_result: GuardCb) -> bool:
        token = request.headers.get('Authorization')
        roles = context.get('roles', [])
        if not token:
            raise UnauthorizedException('Token is required')

        try:
            decoded_token = b64decode(token).decode()
            token_data = json.loads(decoded_token)
            if token_data.get('role') in roles:
                set_result({'user': User(**token_data)})
                return True
            else:
                return False
        except Exception:
            return False


def roles(*role_list: str) -> Callable:
    def wrapper(fn: Callable) -> Callable:
        return meta({'roles': list(role_list)})(fn)

    return wrapper


@controller('/secure')
@use_guard(AuthGuard)
class Controller:
    @get('/')
    @roles('admin', 'superuser')
    def annotated(self, user: Annotated[User, GuardExtra]) -> dict:
        return {'message': "You're allowed to see this because your role is " + user.role}

    @get('/typed')
    @roles('admin', 'superuser')
    def get_typed(self, guard_result: GuardExtra) -> dict:
        user: User = guard_result['user']
        return {'message': "You're allowed to see this because your role is " + user.role}


@module(controllers=[Controller])
class AppModule:
    pass


def bootstrap_app() -> PestApplication:
    app = Pest.create(root_module=AppModule)
    return app

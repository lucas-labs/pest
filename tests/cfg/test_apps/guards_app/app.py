import json
from base64 import b64decode, b64encode
from dataclasses import asdict, dataclass
from typing import Callable, Optional

from fastapi import Body, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from pest import (
    Guard,
    GuardCb,
    GuardCtx,
    GuardExtra,
    Pest,
    controller,
    get,
    meta,
    module,
    post,
    use_guard,
)
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


auth_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login_form')


class AuthGuard(Guard):
    async def can_activate(
        self, request: Request, *, context: GuardCtx, set_result: GuardCb
    ) -> bool:
        token = context.dep('token')
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


class LoginDTO(BaseModel):
    username: str
    password: str


class AuthToken(BaseModel):
    access_token: str
    token_type: str = Field(default='bearer')


def authenticate(username: str, password: str) -> Optional[User]:
    if username == 'mr.spock' and password == 'fascinating':  # noqa: S105
        return User(id=1, name='Mr. Spock', role='admin')
    if username == 'captain.kirk' and password == 'beammeupscotty':  # noqa: S105
        return User(id=2, name='Captain Kirk', role='superuser')
    return None


@controller('/auth', tags=['auth'])
class AuthController:
    @post('/login_form')
    def login_form(self, payload: Annotated[OAuth2PasswordRequestForm, Depends()]) -> AuthToken:
        """login form"""
        user = authenticate(payload.username, payload.password)
        if not user:
            raise UnauthorizedException('Invalid credentials')
        # cheap token... here we should use JWT or something like that, but... testing purposes
        token = b64encode(json.dumps(asdict(user)).encode()).decode()
        return AuthToken(access_token=token)

    @post('/login')
    def login(self, payload: LoginDTO = Body(...)) -> AuthToken:
        """api login endpoint"""
        user = authenticate(payload.username, payload.password)
        if not user:
            raise UnauthorizedException('Invalid credentials')
        # cheap token... here we should use JWT or something like that, but... testing purposes
        token = b64encode(json.dumps(asdict(user)).encode()).decode()
        return AuthToken(access_token=token)


@controller('/secure', tags=['secure'])
@use_guard(AuthGuard, token=auth_scheme)
class ProtectedController:
    @get('/')
    @roles('admin', 'superuser')
    def annotated(self, user: Annotated[User, GuardExtra]) -> dict:
        return {'message': f'Hello {user.role} {user.name}'}

    @get('/typed')
    @roles('admin', 'superuser')
    def get_typed(self, guard_result: GuardExtra) -> dict:
        user: User = guard_result['user']
        return {'message': f'Hello {user.role} {user.name}'}


@module(controllers=[AuthController, ProtectedController])
class AppModule:
    pass


def bootstrap_app() -> PestApplication:
    app = Pest.create(root_module=AppModule)
    return app

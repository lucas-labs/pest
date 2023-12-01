from typing import Annotated

from fastapi import Depends, Request, Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from pest.decorators.controller import controller
from pest.decorators.handler import get
from pest.decorators.module import module
from pest.exceptions.http.http import ForbiddenException, UnauthorizedException

auth_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login_form')


class User(BaseModel):
    email: str
    roles: list[str] = []


def decode_token(token: str) -> User:
    if token == 'admin':  # noqa: S105
        return User(email='foo@bar.com', roles=['admin'])
    if token == 'user':  # noqa: S105
        return User(email='bar@qux.com', roles=['user'])
    raise Exception('Invalid token')


class AuthGuard:
    def __init__(self, roles: list[str] = []) -> None:
        self.allowed_roles = roles or []

    async def __call__(self, token: str = Depends(auth_scheme)) -> User | None:
        try:
            user = decode_token(token)
        except Exception as e:
            # 401 Unauthorized, invalid token
            raise UnauthorizedException(' '.join(e.args) if len(e.args) > 0 else None)

        can_access = len(self.allowed_roles) == 0 or any(
            role in user.roles for role in self.allowed_roles
        )

        if not can_access:
            raise ForbiddenException()  # 403 Forbidden

        return user


def get_me(request: Request, response: Response) -> User:
    response.headers['X-User-Id'] = '1'
    # try:
    return decode_token(request.headers['Authorization'].split(' ')[1])
    # except Exception as e:
    #     raise UnauthorizedException(' '.join(e.args) if len(e.args) > 0 else None)


@controller('/users')
class UsersController:
    @get('/')
    def get_all(self, user: User = Depends(AuthGuard(roles=['admin']))):
        assert isinstance(user, User)
        return [{'email': 'qwert@fake.com'}, {'email': 'asdfg@hjkl.com'}]

    @get('/me')
    def get_me(self, user: Annotated[User, Depends(get_me)]):
        assert isinstance(user, User)
        return user


@module(controllers=[UsersController])
class FastApiDependenciesModule:
    pass

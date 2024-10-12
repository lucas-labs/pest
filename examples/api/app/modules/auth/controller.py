from hashlib import sha256
from time import time

from pydantic import BaseModel

from pest import controller, post
from pest.exceptions import UnauthorizedException

from .db.session import User
from .service import AuthService


class LoginBodyReq(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str

    @classmethod
    def from_user(cls, user: User) -> 'LoginResponse':
        token = sha256(f'{user.username}{time()}'.encode()).hexdigest()
        return cls(token=token)


@controller('/auth', tags=['Auth'])
class AuthController:
    auth: AuthService  # 💉 automatically injected

    @post('/login')
    async def login(self, dto: LoginBodyReq) -> LoginResponse:
        user = await self.auth.login(dto.username, dto.password)
        if not user:
            raise UnauthorizedException('Invalid credentials')

        return LoginResponse.from_user(user)

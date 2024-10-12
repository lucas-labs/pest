import uuid
from typing import Any, AsyncGenerator

from pydantic import BaseModel, Field


class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=50)


USERS = [
    User(username='mr.spock', password='f4sc1n4t1ng'),  # noqa: S106
    User(username='captain.kirk', password='b34m-m3-up-sc077y'),  # noqa: S106
    User(username='captain.picard', password='m4k3-1t-s0'),  # noqa: S106
]


class Session:
    id: uuid.UUID
    connected: bool = False

    def __init__(self) -> None:
        self.id = uuid.uuid4()

    def disconnect(self) -> None:
        print(f'Disconnecting session {self.id}')
        self.connected = False

    def connect(self) -> None:
        print(f'Connecting session {self.id}')
        self.connected = True

    async def __aenter__(self) -> 'Session':
        self.connect()
        return self

    async def __aexit__(self, _exc_type: Any, _exc_value: Any, _traceback: Any) -> None:
        self.disconnect()

    async def select_user_where_username_eq(self, username: str) -> User | None:
        if not self.connected:
            raise Exception('Session is disconnected')

        for user in USERS:
            if user.username == username:
                return user
        return None


# session generator
async def get_session() -> AsyncGenerator[Session, None]:
    async with Session() as session:
        yield session

from uuid import uuid4

from pest.decorators.module import module
from pest.metadata.types.module_meta import ValueProvider

from .data.data import TodoRepo
from .modules.todo.module import TodoModule


class IdGenerator:
    def __call__(self) -> str:
        return str(uuid4())


@module(
    imports=[TodoModule],
    controllers=[],
    providers=[IdGenerator, ValueProvider(provide=TodoRepo, use_value=TodoRepo())],
)
class AppModule:
    pass

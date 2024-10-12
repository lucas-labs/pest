from pest.decorators.module import module
from pest.metadata.types.injectable_meta import ValueProvider

from .data.data import TodoRepo
from .modules.auth._module import AuthModule
from .modules.todo.module import TodoModule


@module(
    imports=[TodoModule, AuthModule],
    providers=[
        # singleton
        ValueProvider(provide=TodoRepo, use_value=TodoRepo())
    ],
)
class AppModule:
    pass

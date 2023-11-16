from pest.decorators.module import module
from pest.metadata.types.module_meta import ValueProvider

from .data.data import TodoRepo
from .modules.todo.module import TodoModule


@module(
    imports=[TodoModule],
    controllers=[],
    providers=[
        ValueProvider(
            provide=TodoRepo,
            use_value=TodoRepo()
        )
    ],
)
class AppModule:
    pass

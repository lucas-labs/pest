from pest.decorators.module import module

from .controllers.root_controller import RootController
from .controllers.todo_controller import TodoController
from .services.todo_service import TodoService


@module(
    controllers=[TodoController, RootController],
    providers=[TodoService],
    exports=[TodoService],
)
class TodoModule:
    pass

from pest.decorators.module import module

from .controllers.todo_controller import TodoController
from .services.todo_service import TodoService


@module(
    controllers=[TodoController],
    providers=[TodoService],
    exports=[TodoService],
)
class TodoModule:
    pass

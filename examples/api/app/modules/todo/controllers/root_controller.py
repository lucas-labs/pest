from typing import Annotated, List, TypeAlias, cast

from fastapi import Path

# from loguru import logger
from pest.decorators.controller import controller
from pest.decorators.handler import get

from ..models.todo import ReadTodoModel
from ..services.todo_service import TodoService

IdPathParam: TypeAlias = Annotated[int, Path(description='''A todo's **unique** identifier''')]


@controller('', tags=['Root'])
class RootController:
    todos: TodoService  # 💉 automatically injected

    @get('/')
    def get_all_todos(self) -> List[ReadTodoModel]:
        # logger.info('Getting all todos')
        return cast(List[ReadTodoModel], self.todos.get_all())

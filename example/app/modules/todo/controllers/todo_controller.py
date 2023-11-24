
from typing import Annotated, TypeAlias, cast

from fastapi import Path

# from loguru import logger
from pest.decorators.controller import controller
from pest.decorators.handler import delete, get, patch, post

from ..models.todo import ReadTodoModel, TodoCreate, TodoModel, TodoUpdate
from ..services.todo_service import TodoService

IdPathParam: TypeAlias = Annotated[int, Path(description='''A todo's **unique** identifier''')]


@controller('/todo', tags=['Todo'])
class TodoController:
    todos: TodoService  # 💉 automatically injected

    @get('/')
    def get_all_todos(self) -> list[ReadTodoModel]:
        # logger.info('Getting all todos')
        return cast(
            list[ReadTodoModel],
            self.todos.get_all()
        )

    @get('/{id}', name='OpenAPI Name Change')
    def get_todo_by_id(self, id: IdPathParam) -> TodoModel:
        """
        ### Get a todo by `id`.

        **Markdown** here will be used as a description
        in the OpenAPI docs.
        """
        return self.todos.get(id)

    @post('/')
    def create_new_todo(self, todo: TodoCreate) -> TodoModel:
        return self.todos.create(todo)

    @delete('/{id}')
    def delete_todo_by_id(self, id: int) -> TodoModel:
        return self.todos.delete(id)

    @patch('/{id}')
    def update_todo_by_id(self, id: int, partial: TodoUpdate) -> TodoModel:
        if partial.done is True:
            return self.todos.mark_complete(id)
        else:
            return self.todos.mark_incomplete(id)

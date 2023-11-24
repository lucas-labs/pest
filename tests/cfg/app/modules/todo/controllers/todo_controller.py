from typing import cast

from pest.decorators.controller import controller
from pest.decorators.handler import delete, get, patch, post

from ..models.todo import ReadTodoModel, TodoCreate, TodoModel, TodoUpdate
from ..services.todo_service import TodoService


@controller('/todo')
class TodoController:
    todos: TodoService

    @get('/')
    def get_all_todos(self) -> list[ReadTodoModel]:
        return cast(list[ReadTodoModel], self.todos.get_all())

    @get('/{id}')
    def get_todo_by_id(self, id: int) -> TodoModel:
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

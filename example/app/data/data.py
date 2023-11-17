from typing import List

from ..modules.todo.models.todo import TodoCreate, TodoModel

default_todos = [
    TodoModel(
        id=1,
        title='delectus aut autem',
        done=False,
    ),
    TodoModel(
        id=2,
        title='quis ut nam facilis et officia qui',
        done=False,
    ),
    TodoModel(
        id=3,
        title='fugiat veniam minus',
        done=False,
    ),
    TodoModel(
        id=4,
        title='et porro tempora',
        done=True,
    )
]


class TodoRepo:
    todos: List[TodoModel]

    def __init__(self) -> None:
        self.todos = [*default_todos]

    def add(self, todo: TodoCreate) -> TodoModel:
        def next_id() -> int:
            return max([todo.id for todo in self.todos]) + 1

        new_todo = TodoModel(
            **(
                # HACK: model_dump was added in pydantic@2 and will replace dict()
                # from @3x onwards; this is a temporary hack to support both
                # versions until pydantic@2x is widely adopted
                todo.model_dump() if hasattr(todo, 'model_dump') else todo.dict()
            ),
            id=next_id(),
            done=False,
        )
        self.todos.append(new_todo)
        return new_todo

    def get_all(self) -> list[TodoModel]:
        return self.todos

    def get_by_id(self, id: int) -> TodoModel | None:
        for todo in self.todos:
            if todo.id == id:
                return todo
        return None

    def set_done_status(self, id: int, done: bool) -> TodoModel | None:
        todo = self.get_by_id(id)
        if todo is not None:
            todo.done = done
        return todo

    def delete_by_id(self, id: int) -> TodoModel | None:
        todo = self.get_by_id(id)
        if todo is not None:
            self.todos.remove(todo)
        return todo

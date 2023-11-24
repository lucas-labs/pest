import fastapi

from pest.exceptions.http.http import ForbiddenException

from ....data.data import TodoRepo
from ..models.todo import TodoCreate, TodoModel


def validate(todo: TodoModel | None) -> TodoModel:
    if todo is None:
        raise fastapi.HTTPException(
            status_code=404,
            detail='Todo not found',
        )
    return todo


class TodoService:
    repo: TodoRepo  # <- automatically injected

    def get_all(self) -> list[TodoModel]:
        return self.repo.get_all()

    def get(self, id: int) -> TodoModel:
        if id == 10:
            # nestjs style http exception raising
            raise ForbiddenException('Number 10 is reserved for Lionel Messi only')

        if id == 11:
            # to test default exception handler
            raise Exception('This is a test exception')

        return validate(self.repo.get_by_id(id))

    def create(self, todo: TodoCreate) -> TodoModel:
        return self.repo.add(todo)

    def delete(self, id: int) -> TodoModel:
        return validate(self.repo.delete_by_id(id))

    def mark_complete(self, id: int) -> TodoModel:
        return validate(self.repo.set_done_status(id, True))

    def mark_incomplete(self, id: int) -> TodoModel:
        return validate(self.repo.set_done_status(id, False))

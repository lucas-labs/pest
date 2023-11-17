from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    id: int = Field(..., gt=0, title='ID of the todo')


class TodoCreate(BaseModel):
    title: str = Field(..., title='Title of the todo')


class TodoUpdate(BaseModel):
    done: bool = Field(..., title='Is it completed?')


class TodoModel(TodoBase, TodoCreate, TodoUpdate):
    pass


class ReadTodoModel(TodoModel):
    id: int = Field(..., exclude=True)

from fastapi.testclient import TestClient

from pest.core.application import PestApplication

from .cfg.app.data.data import TodoRepo
from .cfg.app.modules.todo.services.todo_service import TodoService


def test_global_app_provider(app_n_client: tuple[PestApplication, TestClient]) -> None:
    """🐀 app :: providers :: should add metadata to the decorated class"""
    app, _ = app_n_client

    repo = app.resolve(TodoRepo)
    assert isinstance(repo, TodoRepo)

    # check that the repo is a singleton
    repo2 = app.resolve(TodoRepo)
    assert id(repo) == id(repo2)

    # get service from TodoModule (inner module)
    service = app.resolve(TodoService)
    assert isinstance(service, TodoService)


def test_fastapi_handlers(app_n_client: tuple[PestApplication, TestClient]) -> None:
    """🐀 app :: handlers :: should respond http requests"""
    _, client = app_n_client

    # get without path param
    response = client.get('/todo')
    assert response.status_code == 200
    all_todos = response.json()
    assert isinstance(all_todos, list)
    assert len(all_todos) > 0

    length = len(all_todos)

    # get with path param
    response = client.get('/todo/1')
    assert response.status_code == 200
    todo_one = response.json()
    assert isinstance(todo_one, dict)
    assert todo_one['id'] == 1
    assert todo_one['done'] is False

    # post (create)
    response = client.post('/todo', json={'title': 'new todo'})
    assert response.status_code == 200
    new_todo = response.json()
    assert isinstance(new_todo, dict)
    assert new_todo['title'] == 'new todo'
    assert new_todo['done'] is False
    assert new_todo['id'] == len(all_todos) + 1

    # get all again
    response = client.get('/todo')
    all_again = response.json()
    assert len(all_again) == length + 1

    # patch (update)
    response = client.patch('/todo/1', json={'done': True})
    assert response.status_code == 200
    todo_one = response.json()
    assert isinstance(todo_one, dict)
    assert todo_one['id'] == 1
    assert todo_one['done'] is True

    # delete
    response = client.delete('/todo/1')
    assert response.status_code == 200
    todo_one = response.json()
    assert isinstance(todo_one, dict)
    assert todo_one['id'] == 1

    # get all again
    response = client.get('/todo')
    all_again = response.json()
    assert len(all_again) == length

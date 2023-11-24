from datetime import datetime

from fastapi import Request, Response
from fastapi.testclient import TestClient

from pest.core.application import PestApplication
from pest.factory import Pest
from pest.middleware.base import CallNext, PestMiddleware, PestMiddlwareCallback, inject

from .cfg.app.app_module import AppModule, IdGenerator
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


def test_pest_functional_middleware_cb() -> None:
    """🐀 app :: middleware :: should execute middleware on each reaquest"""

    async def pest_middleware(request: Request, call_next: CallNext) -> Response:
        response = await call_next(request)
        response.headers['X-Process-Time'] = datetime.now().isoformat()
        return response

    app = Pest.create(AppModule, middleware=[pest_middleware])
    client = TestClient(app)

    response = client.get('/todo')
    assert 'X-Process-Time' in response.headers
    time_1 = response.headers['X-Process-Time']

    response = client.get('/todo')
    assert 'X-Process-Time' in response.headers
    time_2 = response.headers['X-Process-Time']

    assert time_1 != time_2


def test_pest_functional_middleware_cb_with_di():
    """🐀 app :: middleware ::
    should allow injection into functional middlewares as function parameters
    """

    # = inject() is a dummy method, necessary for injecting dependencies into
    # functional pest middlewares, it wouldn't be necessary if we were using
    # class-based pest middlewares
    async def pest_middleware(
        request: Request, call_next: CallNext, id_gen: IdGenerator = inject()
    ) -> Response:
        response = await call_next(request)
        response.headers['X-Request-Id'] = id_gen()
        return response

    app = Pest.create(AppModule, middleware=[pest_middleware])
    client = TestClient(app)

    response = client.get('/todo')
    assert 'X-Request-Id' in response.headers
    id_1 = response.headers['X-Request-Id']

    response = client.get('/todo')
    assert 'X-Request-Id' in response.headers
    id_2 = response.headers['X-Request-Id']

    assert id_1 != id_2


def test_pest_class_based_middleware_cb() -> None:
    """🐀 app :: middleware :: should execute class based middleware on each reaquest"""

    class MiddlewareCallback(PestMiddlwareCallback):
        async def __call__(self, request: Request, call_next: CallNext) -> Response:
            response = await call_next(request)
            response.headers['X-Process-Time'] = datetime.now().isoformat()
            return response

    app = Pest.create(AppModule, middleware=[MiddlewareCallback])
    client = TestClient(app)

    response = client.get('/todo')
    assert 'X-Process-Time' in response.headers
    time_1 = response.headers['X-Process-Time']

    response = client.get('/todo')
    assert 'X-Process-Time' in response.headers
    time_2 = response.headers['X-Process-Time']

    assert time_1 != time_2


def test_pest_class_based_middleware_with_di() -> None:
    """🐀 app :: middleware :: should allow injection into class middlewares"""

    class MiddlewareCallback(PestMiddlwareCallback):
        id_gen: IdGenerator  # 💉 automatically injected

        async def __call__(self, request: Request, call_next: CallNext) -> Response:
            response = await call_next(request)
            response.headers['X-Request-Id'] = self.id_gen()
            return response

    app = Pest.create(AppModule, middleware=[MiddlewareCallback])
    client = TestClient(app)

    response = client.get('/todo')
    assert 'X-Request-Id' in response.headers
    id_1 = response.headers['X-Request-Id']

    response = client.get('/todo')
    assert 'X-Request-Id' in response.headers
    id_2 = response.headers['X-Request-Id']

    assert id_1 != id_2


def test_pest_class_middleware() -> None:
    """🐀 app :: middleware :: should allow defining a middleware using Pest style"""

    class Middlware(PestMiddleware):
        async def use(self, request: Request, callx_next: CallNext) -> Response:
            response = await callx_next(request)
            response.headers['X-Process-Time'] = datetime.now().isoformat()
            return response

    assert issubclass(Middlware, PestMiddleware)

    app = Pest.create(AppModule, middleware=[Middlware])
    client = TestClient(app)

    response = client.get('/todo')
    assert 'X-Process-Time' in response.headers
    time_1 = response.headers['X-Process-Time']

    response = client.get('/todo')
    assert 'X-Process-Time' in response.headers
    time_2 = response.headers['X-Process-Time']

    assert time_1 != time_2


def test_pest_class_middleware_with_di() -> None:
    """🐀 app :: middleware ::
    should allow defining a middleware using Pest style and injecting dependencies
    """

    class Middlware(PestMiddleware):
        id_gen: IdGenerator  # 💉 automatically injected

        async def use(self, request: Request, callx_next: CallNext) -> Response:
            response = await callx_next(request)
            response.headers['X-Request-Id'] = self.id_gen()
            return response

    assert issubclass(Middlware, PestMiddleware)

    app = Pest.create(AppModule, middleware=[Middlware])
    client = TestClient(app)

    response = client.get('/todo')
    assert 'X-Request-Id' in response.headers
    id_1 = response.headers['X-Request-Id']

    response = client.get('/todo')
    assert 'X-Request-Id' in response.headers
    id_2 = response.headers['X-Request-Id']

    assert id_1 != id_2

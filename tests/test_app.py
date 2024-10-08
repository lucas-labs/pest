from datetime import datetime

import pytest
from fastapi import Request, Response
from fastapi.testclient import TestClient
from pytest import raises

from pest.core.application import root_module
from pest.di import inject
from pest.factory import Pest
from pest.middleware.base import CallNext, PestMiddleware, PestMiddlwareCallback

from .cfg.test_apps.multi_singleton_app.app_module import Repo1, Repo2
from .cfg.test_apps.todo_app.app_module import AppModule, IdGenerator
from .cfg.test_apps.todo_app.data.data import TodoRepo
from .cfg.test_apps.todo_app.modules.todo.services.todo_service import TodoService


@pytest.mark.asyncio
async def test_global_app_provider(app_n_client) -> None:
    """🐀 app :: providers :: should add metadata to the decorated class"""
    app, _ = app_n_client

    repo = app.resolve(TodoRepo)
    assert isinstance(repo, TodoRepo)

    # check that the repo is a singleton
    repo2 = app.resolve(TodoRepo)
    assert id(repo) == id(repo2)

    # get service from TodoModule (inner module)
    service = await app.aresolve(TodoService)
    assert isinstance(service, TodoService)


def test_fastapi_handlers(app_n_client) -> None:
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
    should allow injection into functional middlewares as handler parameters
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


def test_app_params_path_as_var(fastapi_params_app):
    """🐀 app :: params :: should allow using path params as handler parameters"""

    _, client = fastapi_params_app

    response = client.get('/path/as_var/1')
    assert response.status_code == 200
    assert response.json() == {'name': 'foo', 'job': 'dev'}


def test_app_params_path_as_typed_var(fastapi_params_app):
    """🐀 app :: params :: should allow using typed path params as handler parameters"""

    _, client = fastapi_params_app

    response = client.get('/path/as_typed_var/1')
    assert response.status_code == 200
    assert response.json() == {'name': 'foo', 'job': 'dev'}


def test_app_params_predefine_value(fastapi_params_app):
    """🐀 app :: params :: should allow using predefine values"""

    _, client = fastapi_params_app

    response = client.get('/path/predefine_value/foo')
    assert response.status_code == 200
    assert response.json() == {'name': 'foo', 'job': 'dev'}


def test_app_params_annotated(fastapi_params_app):
    """🐀 app :: params :: should allow using annotated params"""

    _, client = fastapi_params_app

    response = client.get('/path/annotated/1')
    assert response.status_code == 200
    assert response.json() == {'name': 'foo', 'job': 'dev'}


def test_app_params_annotated_validation_error(fastapi_params_app):
    """🐀 app :: params :: should raise validation error when annotated params are invalid"""

    _, client = fastapi_params_app

    response = client.get('/path/annotated/0')
    assert response.status_code == 400

    response_body: dict = response.json()
    assert response_body.get('message', None) is not None
    message = response_body['message']

    assert 'should be greater than 0' in message[0]


def test_app_query_params_as_var(fastapi_params_app):
    """🐀 app :: query params :: should allow using query params as handler parameters"""

    _, client = fastapi_params_app

    response = client.get('/query/as_var?id=1')
    assert response.status_code == 200
    assert response.json() == {'name': 'foo', 'job': 'dev'}


def test_app_query_params_as_typed_var(fastapi_params_app):
    """🐀 app :: query params :: should allow using typed query params as handler parameters"""

    _, client = fastapi_params_app

    response = client.get('/query/as_typed_var?id=1')
    assert response.status_code == 200
    assert response.json() == {'name': 'foo', 'job': 'dev'}


def test_app_query_params_optional(fastapi_params_app):
    """🐀 app :: query params :: should allow using optional query params as handler parameters"""

    _, client = fastapi_params_app

    response = client.get('/query/optional')
    assert response.status_code == 200
    assert response.json() == {'message': 'id is not provided'}

    response = client.get('/query/optional?id=1')
    assert response.status_code == 200
    assert response.json() == {'name': 'foo', 'job': 'dev'}


def test_app_query_params_annotated(fastapi_params_app):
    """🐀 app :: query params :: should allow using annotated query params as handler parameters"""

    _, client = fastapi_params_app

    response = client.get('/query/annotated?id=1')
    assert response.status_code == 200
    assert response.json() == {'name': 'foo', 'job': 'dev'}


def test_app_query_params_annotated_validation_error(fastapi_params_app):
    """🐀 app :: query params ::
    should raise validation error when annotated query params are invalid
    """

    _, client = fastapi_params_app

    response = client.get('/query/annotated?id=0')
    assert response.status_code == 400

    response_body: dict = response.json()
    assert response_body.get('message', None) is not None
    message = response_body['message']

    assert 'should be greater than 0' in message[0]


def test_app_body(fastapi_params_app):
    """🐀 app :: body :: should allow using body as handler parameters"""

    _, client = fastapi_params_app

    response = client.post('/body/as_typed_var', json={'id': '3', 'name': 'qux', 'job': 'dev'})
    assert response.status_code == 200
    assert response.json() == {'id': 3, 'name': 'qux', 'job': 'dev'}


def test_app_body_validation_error(fastapi_params_app):
    """🐀 app :: body :: should raise validation error when body is invalid"""

    _, client = fastapi_params_app

    response = client.post('/body/as_typed_var', json={'id': '0', 'name': 'qux', 'job': 'dev'})
    assert response.status_code == 400

    response_body: dict = response.json()
    assert response_body.get('message', None) is not None
    message = response_body['message']

    assert 'should be greater than 0' in message[0]


def test_app_body_optional(fastapi_params_app):
    """🐀 app :: body :: should not fail for optional body fields"""

    _, client = fastapi_params_app

    response = client.post('/body/as_typed_var', json={'id': '3', 'name': 'qux'})
    assert response.status_code == 200
    assert response.json() == {'id': 3, 'name': 'qux', 'job': None}


def test_app_body_annotated(fastapi_params_app):
    """🐀 app :: body :: should allow using annotated body as handler parameters"""

    _, client = fastapi_params_app

    response = client.post('/body/annotated', json={'id': '3', 'name': 'qux', 'job': 'dev'})
    assert response.status_code == 200
    assert response.json() == {'id': 3, 'name': 'qux', 'job': 'dev'}


def test_app_body_annotated_validation_error(fastapi_params_app):
    """🐀 app :: body ::
    should raise validation error when annotated body is invalid
    """

    _, client = fastapi_params_app

    response = client.post('/body/annotated', json={'id': '0', 'name': 'qux', 'job': 'dev'})
    assert response.status_code == 400

    response_body: dict = response.json()
    assert response_body.get('message', None) is not None
    message = response_body['message']

    assert 'should be greater than 0' in message[0]


def test_app_body_fields_annotated(fastapi_params_app):
    """🐀 app :: body ::
    should allow using annotated body fields as handler parameters
    """

    _, client = fastapi_params_app

    response = client.post('/body/body_fields', json={'id': '3', 'name': 'qux'})
    assert response.status_code == 200
    assert response.json() == {'id': 3, 'name': 'qux'}


def test_app_body_fields_validation_error(fastapi_params_app):
    """🐀 app :: body ::
    should raise validation error when annotated body fields are invalid
    """

    _, client = fastapi_params_app

    response = client.post('/body/body_fields', json={'id': '0', 'name': 'qux'})
    assert response.status_code == 400

    response_body: dict = response.json()
    assert response_body.get('message', None) is not None
    message = response_body['message']

    assert 'should be greater than 0' in message[0]


def test_app_body_fields_optional(fastapi_params_app):
    """🐀 app :: body ::
    should not fail for optional annotated body fields
    """

    _, client = fastapi_params_app

    response = client.post('/body/body_fields', json={'id': '3'})
    assert response.status_code == 200
    assert response.json() == {'id': 3, 'name': None}


def test_app_request(fastapi_params_app):
    """🐀 app :: request :: should allow using raw request as handler parameters"""

    _, client = fastapi_params_app

    response = client.get('/request/ping', headers={'X-Client': 'pinger'})
    assert response.status_code == 200
    assert response.json() == {'pong_to': 'pinger'}
    assert response.headers['X-Server'] == 'ponger'


def test_app_dependencies(fastapi_dependencies_app):
    """🐀 app :: dependencies ::
    should allow using fastapi dependencies as handler parameters
    """

    _, client = fastapi_dependencies_app

    response = client.get('/users', headers={'Authorization': 'Bearer admin'})
    assert response.status_code == 200
    body = response.json()

    assert body == [{'email': 'qwert@fake.com'}, {'email': 'asdfg@hjkl.com'}]


def test_app_dependencies_exception(fastapi_dependencies_app):
    """🐀 app :: dependencies ::
    should return valid error response when fastapi dependencies raise exceptions
    """

    _, client = fastapi_dependencies_app

    response = client.get('/users')
    assert response.status_code == 401
    body = response.json()

    assert body == {
        'code': 401,
        'error': 'Unauthorized',
        'message': 'Not authenticated',
    }


def test_app_request_access_on_dependencies(fastapi_dependencies_app):
    """🐀 app :: dependencies :: should allow using request and response in dependency functions"""

    _, client = fastapi_dependencies_app

    response = client.get('/users/me', headers={'Authorization': 'Bearer admin'})
    assert response.status_code == 200
    assert response.headers['X-User-Id'] == '1'
    body = response.json()

    assert body == {
        'email': 'foo@bar.com',
        'roles': ['admin'],
    }


def test_app_request_dependency_exception(fastapi_dependencies_app):
    """🐀 app :: dependencies :: should return valid error response when server Exception"""

    _, client = fastapi_dependencies_app

    with raises(Exception) as excinfo:
        client.get('/users/me', headers={'Authorization': 'Bearer invalid'})

    assert excinfo.value.args[0] == 'Invalid token'


@pytest.mark.asyncio
async def test_multiple_singletons_resolves_ok(multiple_singletons_app) -> None:
    """🐀 app :: dependencies :: should resolve multiple singleton independently"""

    # check issue #31
    app, client = multiple_singletons_app

    app_module = root_module(app)
    child_module = app_module.imports[0]

    repo1 = await child_module.aget(Repo1)
    repo2 = await child_module.aget(Repo2)

    assert isinstance(repo1, Repo1)
    assert isinstance(repo2, Repo2)
    assert repo1 != repo2

    r1 = client.get('/ctrl/').json()

    # check that providers are actually singletons
    assert r1['repo1'] != r1['repo2']

    # check that providers are actually singletons
    r2 = client.get('/ctrl/').json()
    assert r1['repo1'] == r2['repo1']
    assert r1['repo2'] == r2['repo2']

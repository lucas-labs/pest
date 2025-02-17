from typing import Any, List, Optional

try:
    from typing import Coroutine
except ImportError:
    from typing_extensions import Coroutine

import pytest
from fastapi.testclient import TestClient

from pest import (
    OnApplicationBootstrap,
    OnModuleInit,
    Pest,
    ValueProvider,
    controller,
    get,
    module,
)
from pest.core.application import PestApplication

# Tracking the order of lifecycle hook calls
LIFECYCLE_CALLS: List[str] = []


@controller('/foo')
class FooController(OnModuleInit, OnApplicationBootstrap):
    def on_module_init(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('FooController.on_module_init')

    def on_application_bootstrap(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('FooController.on_application_bootstrap')

    @get('/')
    def foo(self) -> dict:
        return {'message': 'Hello!'}


class FooService(OnModuleInit, OnApplicationBootstrap):
    def on_module_init(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('FooService.on_module_init')

    def on_application_bootstrap(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('FooService.on_application_bootstrap')


@module(
    controllers=[FooController],
    providers=[ValueProvider(provide=FooService, use_value=FooService())],
)
class AppModule(OnModuleInit, OnApplicationBootstrap):
    def on_module_init(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('AppModule.on_module_init')

    def on_application_bootstrap(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('AppModule.on_application_bootstrap')


@controller('/bar')
class BarController(OnModuleInit, OnApplicationBootstrap):
    def on_module_init(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('BarController.on_module_init')

    def on_application_bootstrap(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('BarController.on_application_bootstrap')

    @get('/')
    def bar(self) -> dict:
        return {'message': 'Bar!'}


class BarService(OnModuleInit, OnApplicationBootstrap):
    def on_module_init(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('BarService.on_module_init')

    def on_application_bootstrap(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('BarService.on_application_bootstrap')


@module(
    controllers=[BarController],
    providers=[ValueProvider(provide=BarService, use_value=BarService())],
    exports=[BarService],
)
class ChildModule(OnModuleInit, OnApplicationBootstrap):
    def on_module_init(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('ChildModule.on_module_init')

    def on_application_bootstrap(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('ChildModule.on_application_bootstrap')


@module(
    imports=[ChildModule],
    controllers=[FooController],
    providers=[ValueProvider(provide=FooService, use_value=FooService())],
)
class RootModule(OnModuleInit, OnApplicationBootstrap):
    def on_module_init(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('RootModule.on_module_init')

    def on_application_bootstrap(self) -> Optional[Coroutine[Any, Any, None]]:
        LIFECYCLE_CALLS.append('RootModule.on_application_bootstrap')


@pytest.fixture(autouse=True)
def clear_lifecycle_calls():
    LIFECYCLE_CALLS.clear()
    yield


@pytest.fixture()
def simple_app() -> tuple[PestApplication, TestClient]:
    app = Pest.create(root_module=AppModule)
    with TestClient(app) as client:
        return app, client


@pytest.fixture()
def nested_app() -> tuple[PestApplication, TestClient]:
    app = Pest.create(root_module=RootModule)
    with TestClient(app) as client:
        return app, client


@pytest.mark.asyncio
async def test_simple_app_lifecycle_hooks(simple_app) -> None:
    """🐀 lifecycle :: hooks :: should be called in correct order in simple app"""
    app, client = simple_app

    # Test that all endpoints work
    response = client.get('/foo/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello!'}

    # Verify lifecycle hooks were called in correct order
    assert LIFECYCLE_CALLS == [
        # Module Init Phase
        'FooService.on_module_init',  # First providers
        'FooController.on_module_init',  # Then controllers
        'AppModule.on_module_init',  # Finally the module itself
        # Application Bootstrap Phase
        'FooService.on_application_bootstrap',  # First providers
        'FooController.on_application_bootstrap',  # Then controllers
        'AppModule.on_application_bootstrap',  # Finally the module itself
    ]


@pytest.mark.asyncio
async def test_nested_modules_lifecycle_hooks(nested_app) -> None:
    """🐀 lifecycle :: hooks :: should be called in correct order with nested modules"""
    app, client = nested_app

    # Test that all endpoints work
    response = client.get('/foo/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello!'}

    response = client.get('/bar/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Bar!'}

    # Verify lifecycle hooks were called in correct order
    assert LIFECYCLE_CALLS == [
        # Child Module Init Phase
        'BarService.on_module_init',  # Child module providers
        'BarController.on_module_init',  # Child module controllers
        'ChildModule.on_module_init',  # Child module itself
        # Root Module Init Phase
        'FooService.on_module_init',  # Root module providers
        'FooController.on_module_init',  # Root module controllers
        'RootModule.on_module_init',  # Root module itself
        # Application Bootstrap Phase (bottom-up)
        'BarService.on_application_bootstrap',  # Child providers
        'BarController.on_application_bootstrap',  # Child controllers
        'ChildModule.on_application_bootstrap',  # Child module
        'FooService.on_application_bootstrap',  # Root providers
        'FooController.on_application_bootstrap',  # Root controllers
        'RootModule.on_application_bootstrap',  # Root module
    ]


@pytest.mark.asyncio
async def test_async_lifecycle_hooks() -> None:
    """🐀 lifecycle :: hooks :: should work with async lifecycle hooks"""
    LIFECYCLE_CALLS.clear()

    @controller('/async')
    class AsyncController(OnModuleInit, OnApplicationBootstrap):
        async def on_module_init(self) -> None:
            LIFECYCLE_CALLS.append('AsyncController.on_module_init')

        async def on_application_bootstrap(self) -> None:
            LIFECYCLE_CALLS.append('AsyncController.on_application_bootstrap')

        @get('/')
        def handler(self) -> dict:
            return {'message': 'Async!'}

    class AsyncService(OnModuleInit, OnApplicationBootstrap):
        async def on_module_init(self) -> None:
            LIFECYCLE_CALLS.append('AsyncService.on_module_init')

        async def on_application_bootstrap(self) -> None:
            LIFECYCLE_CALLS.append('AsyncService.on_application_bootstrap')

    @module(
        controllers=[AsyncController],
        providers=[ValueProvider(provide=AsyncService, use_value=AsyncService())],
    )
    class AsyncModule(OnModuleInit, OnApplicationBootstrap):
        async def on_module_init(self) -> None:
            LIFECYCLE_CALLS.append('AsyncModule.on_module_init')

        async def on_application_bootstrap(self) -> None:
            LIFECYCLE_CALLS.append('AsyncModule.on_application_bootstrap')

    app = Pest.create(root_module=AsyncModule)
    with TestClient(app) as client:
        response = client.get('/async/')
        assert response.status_code == 200
        assert response.json() == {'message': 'Async!'}

        assert LIFECYCLE_CALLS == [
            'AsyncService.on_module_init',
            'AsyncController.on_module_init',
            'AsyncModule.on_module_init',
            'AsyncService.on_application_bootstrap',
            'AsyncController.on_application_bootstrap',
            'AsyncModule.on_application_bootstrap',
        ]

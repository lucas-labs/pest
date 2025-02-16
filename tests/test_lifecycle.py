# from typing import Tuple, TypeAlias

# import pytest
# from fastapi.testclient import TestClient

# from pest import (
#     OnApplicationBootstrap,
#     OnModuleInit,
#     Pest,
#     controller,
#     get,
#     module,
# )
# from pest.core.application import PestApplication


# @controller('/foo')
# class FooController(OnModuleInit, OnApplicationBootstrap):
#     @get('/')
#     def foo(self) -> dict:
#         return {'message': 'Hello!'}


# @module(controllers=[FooController])
# class AppModule:
#     pass


# def bootstrap_app() -> PestApplication:
#     app = Pest.create(root_module=AppModule)
#     return app


# TestApp: TypeAlias = Tuple[PestApplication, TestClient]


# @pytest.fixture()
# def lifecycle_app() -> TestApp:
#     app = bootstrap_app()
#     with TestClient(app) as client:
#         return app, client


import pytest


@pytest.mark.asyncio
async def test_something() -> None:
    # app = await bootstrap_app()

    # print(app)
    pass

from enum import Enum
from typing import Union

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from fastapi import Body, Path, Query, Request, Response
from pydantic import BaseModel, Field

from pest.decorators.controller import controller
from pest.decorators.handler import get, post
from pest.decorators.module import module


class BodyParam(BaseModel):
    id: int = Field(gt=0)
    name: Union[str, None] = None
    job: Union[str, None] = None


class Foos(str, Enum):
    FOO = 'foo'
    BAR = 'bar'


foos = {
    1: {'name': Foos.FOO, 'job': 'dev'},
    2: {'name': Foos.BAR, 'job': 'cto'},
}


@controller('/path')
class PathParams:
    @get('/as_var/{id}')
    def as_var(self, id):
        assert isinstance(id, str)
        return foos[int(id)]

    @get('/as_typed_var/{id}')
    def as_typed_var(self, id: int):
        assert isinstance(id, int)
        return foos[id]

    @get('/predefine_value/{name}')
    def predefine_value(self, name: Foos):
        assert isinstance(name, Foos)
        # search it in foos
        for foo in foos.values():
            if foo['name'] == name:
                return foo
        return None

    @get('/annotated/{id}')
    def annotated(self, id: Annotated[int, Path(gt=0)]):
        assert isinstance(id, int)
        assert id > 0
        return foos[id]


@controller('/query')
class QueryParams:
    @get('/as_var')
    def as_var(self, id):
        assert isinstance(id, str)
        return foos[int(id)]

    @get('/as_typed_var')
    def as_typed_var(self, id: int):
        assert isinstance(id, int)
        return foos[id]

    @get('/optional')
    def optional(self, id: Union[int, None] = None):
        if id is None:
            return {'message': 'id is not provided'}

        return self.as_typed_var(id)

    @get('/annotated')
    def annotated(self, id: Annotated[Union[int, None], Query(gt=0)]):
        assert isinstance(id, int)
        assert id > 0
        return foos[id]


@controller('/body')
class BodyParams:
    @post('/as_typed_var')
    def as_var(self, body: BodyParam):
        assert isinstance(body, BodyParam)
        if body.id in foos:
            return {'message': 'id already exists'}
        return body

    @post('/annotated')
    def annotated(self, body: Annotated[BodyParam, Body()]):
        assert isinstance(body, BodyParam)
        if body.id in foos:
            return {'message': 'id already exists'}
        return body

    @post('/body_fields')
    def body_fields(
        self, id: Annotated[int, Body(gt=0)], name: Annotated[Union[str, None], Body()] = None
    ):
        assert isinstance(id, int)
        if name is not None:
            assert isinstance(name, str)
        if id in foos:
            return {'message': 'id already exists'}
        return {'id': id, 'name': name}


@controller('/request')
class RequestParam:
    @get('/ping')
    def ping(self, request: Request, response: Response):
        assert isinstance(request, Request)
        assert isinstance(response, Response)

        client_name = request.headers.get('X-Client')
        response.headers['X-Server'] = 'ponger'

        return {
            'pong_to': client_name,
        }


@module(controllers=[PathParams, QueryParams, BodyParams, RequestParam])
class FastApiParamsModule:
    pass

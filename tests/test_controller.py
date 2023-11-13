

from fastapi.routing import APIRoute

from pest.decorators.controller import controller
from pest.decorators.handler import get
from pest.metadata.meta import META_KEY
from pest.metadata.types._meta import PestType
from pest.primitives.common import primitive_type, status
from pest.primitives.controller import Controller, router_of, setup_controller
from pest.primitives.types.status import Status
from pest.utils.fastapi.router import PestRouter

# aliased porque setup_module es un builtin de pytest


def test_controller_inheritance():
    """🐀 controllers :: @controller :: should make the decorated class inherit from Controller"""
    @controller('/')
    class FooController:
        pass

    assert issubclass(FooController, Controller)
    assert issubclass(FooController, FooController)


def test_controller_meta():
    """🐀 controllers :: @controller :: should add metadata to the decorated class"""
    def cb() -> None:
        pass

    @controller(
        '/test',
        on_startup=[cb],
        on_shutdown=[cb],
        deprecated=True,
        redirect_slashes=True,
        include_in_schema=True,
    )
    class FooController:
        pass

    assert primitive_type(FooController) == PestType.CONTROLLER
    assert hasattr(FooController, META_KEY)
    meta: dict = getattr(FooController, META_KEY)

    assert meta is not None
    assert isinstance(meta, dict)
    assert meta['meta_type'] == PestType.CONTROLLER
    assert meta['prefix'] == '/test'
    assert meta['on_startup'] == [cb]
    assert meta['on_shutdown'] == [cb]
    assert meta['deprecated'] is True
    assert meta['redirect_slashes'] is True


def test_controller_setup():
    """🐀 controllers :: __setup_controller_class__ :: should setup the controller's router"""''
    @controller('/foo')
    class FooController:
        pass

    setup_controller(FooController)

    assert status(FooController) == Status.READY
    router = router_of(FooController)

    assert isinstance(router, PestRouter)
    assert router.prefix == '/foo'


def test_controller_handlers_setup():
    """🐀 controllers :: __setup_controller_class__ :: should setup the controller's handlers"""
    @controller('/foo')
    class FooController:
        @get('/bar')
        def bar_handler(self) -> str:
            return 'bar'

        def no_handler(self) -> str:
            return 'no'

    setup_controller(FooController)
    assert status(FooController) == Status.READY

    router = router_of(FooController)
    assert len(router.routes) == 2

    route = router.routes[0]
    route_slash = router.routes[1]

    assert isinstance(route, APIRoute)
    assert isinstance(route_slash, APIRoute)
    assert route.path == '/foo/bar'
    assert route_slash.path == '/foo/bar/'


# IDEA: actualmente tenemos el problemita de que cuando iniciemos el handler method, hay que
#       inyectarle la clase en su self. Ese self es una dependencia del parámetro y eso
#       es un problema, porque fastapi funciona bien con Depends() pero no con mi
#       implementacion de di. Una buena solución podría ser que en vez de usar container.resolve
#       (que no sé ni cómo hacerlo) usemos algo tipo Depends(resolve_class(cls))
#       donde resolve_class será una función dependencia que depende a su vez de Request.
#       quizá de aquí pueda sacar el modulo de alguna forma y así obtener el container
#       y dentro de mi resolve_class puedo resolver cls usando mi container....
#       Para investigar:
#         - https://fastapi.tiangolo.com/advanced/advanced-dependencies/#parameterized-dependencies
#         - https://github.com/tiangolo/fastapi/blob/480620372a662aa9025c47410fbc90a255b2fc94/fastapi/security/oauth2.py#L473
#             este es un ejemplo de dependencia que depende de Request y está parametrizada (como
#            la que quiero hacer yo con resolve_class(cls), donde cls es el parámetro). Usa un
#            callable instance para lograrlo. Quizá pueda hacer algo similar con mi resolve_class

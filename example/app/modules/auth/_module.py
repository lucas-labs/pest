from pest.decorators.module import module
from pest.metadata.types.injectable_meta import FactoryProvider, Scope

from .controller import AuthController
from .db.session import Session, get_session
from .service import AuthService


@module(
    controllers=[AuthController],
    providers=[
        AuthService,
        FactoryProvider(provide=Session, use_factory=get_session, scope=Scope.SCOPED),
    ],
)
class AuthModule:
    pass

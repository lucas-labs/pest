
from .primitives.application import PestApplication
from .primitives.module import setup_module


class Pest:
    @classmethod
    def create(cls, root_module: type) -> PestApplication:
        """
        🐀 ⇝ creates and initializes a pest application

        :param root_module: the root (entry point) module of the application
        """

        module_tree = setup_module(root_module)
        routers = module_tree.routers
        app = PestApplication(module=module_tree)

        for router in routers:
            app.include_router(router)

        return app

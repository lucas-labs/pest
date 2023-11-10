
from .primitives.module import Module, setup_module


class Pest:
    @classmethod
    def create(cls, root_module: type) -> Module:
        """
        🐀 ⇝ creates and initializes a pest application

        :param root_module: the root (entry point) module of the application
        """

        module_tree = setup_module(root_module)
        return module_tree

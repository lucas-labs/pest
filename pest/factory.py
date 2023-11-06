
from .exceptions.base import PestException
from .metadata.meta import get_meta
from .metadata.types.module_meta import ModuleMeta
from .primitives.module import Module, setup_module


def make_module_tree(clazz: type) -> Module:
    if not issubclass(clazz, Module):
        raise PestException(
            f'{clazz.__name__} is not a module.',
            hint=f'decorate `{clazz.__name__}` with the `@module` decorator (or one of its aliases)'
        )

    module = clazz()
    meta: ModuleMeta = get_meta(clazz, type=ModuleMeta)

    for child in meta.imports if meta.imports else []:
        child_instance = make_module_tree(child)
        module.imports += [child_instance]

    module.providers = meta.providers if meta.providers else []
    module.exports = meta.exports if meta.exports else []
    setup_module(module)

    return module


class Pest:
    @classmethod
    def create(cls, root_module: type) -> Module:
        """
        🐀 ⇝ creates and initializes a pest application

        :param root_module: the root (entry point) module of the application
        """

        module_tree = make_module_tree(root_module)
        return module_tree

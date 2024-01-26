from pest import controller, get, module
from pest.metadata.types.injectable_meta import ValueProvider


class Repo1:
    def get(self):
        return 'this is repo 1'


class Repo2:
    def get(self):
        return 'this is repo 2'


@controller('/ctrl')
class Controller1:
    repo1: Repo1
    repo2: Repo2

    @get('/')
    def get(self):
        return {
            'repo1': id(self.repo1),
            'repo2': id(self.repo2),
        }


@module(controllers=[Controller1])
class ChildModule:
    pass


@module(
    imports=[ChildModule],
    providers=[
        ValueProvider(provide=Repo1, use_value=Repo1()),
        ValueProvider(provide=Repo2, use_value=Repo2()),
    ],
)
class AppModule:
    pass

from ...decorators.module import module
from ...metadata.types.injectable_meta import ValueProvider
from .services.scheduler_explorer import SchedulerExplorer

# TODO: improve task scheduler module
#       this implementation is just a first approach. It works, but it lacks a lot of features.
#       Ideally, it should be able to "register" jobs, start and stop them, and provide a way to
#       manage them. Similar to what NestJS does with its scheduler module.
#       See: https://docs.nestjs.com/techniques/task-scheduling


@module(
    imports=[],
    controllers=[],
    providers=[ValueProvider(provide=SchedulerExplorer, use_value=SchedulerExplorer())],
    exports=[],
)
class ScheduleModule:
    pass

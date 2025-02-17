from datetime import datetime
from typing import Any

from pest import Pest, ValueProvider, controller, get, module
from pest.schedule import ScheduleModule, cron, scheduler


@controller('/foo')
class FooController:
    @get('/')
    def foo(self) -> Any:
        return {'message': 'Hello!'}


@scheduler
class ScheduledTasks:
    counter = 0

    @cron('* * * * *')  # every minute
    async def task(self) -> None:
        self.counter += 1
        print(f'#{self.counter} hello from cron job at {datetime.now().isoformat()}')


@module(
    providers=[ValueProvider(provide=ScheduledTasks, use_value=ScheduledTasks())],
    exports=[ScheduledTasks],
)
class JobsModule:
    pass


@module(
    controllers=[FooController],
    imports=[ScheduleModule, JobsModule],
)
class AppModule:
    pass


app = Pest.create(AppModule)

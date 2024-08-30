from typing import Callable, Type, TypeVar, Union, cast

T = TypeVar('T')


class _Inject:
    """
    Class used to inject dependencies from the `module`'s container.
    @internal you should not use this class directly, use `inject` instead.
    """

    def __init__(self, token: Union[Type, None, Callable]) -> None:
        self.token = token


def inject(token: Union[None, Type[T], Callable] = None) -> T:
    """
    🐀 ⇝ marks a parameter as a dependency to be injected by `pest` 💉

    Similar to `fastapi.Depends` but this one is used to inject dependencies
    from the `module`'s private container, respecting encapsulation.

    #### Example

    ```py
    @get('/{user_id}')
    def get_user(self, user_id: str, svc: Annotated[Service, inject]):
        return svc.get_user(user_id)
    ```

    You can also use it without the `Annotated` annotation:

    ```py
    svc: Service = inject()

    # or even like this if you don't care about type hints
    svc = inject(Service)
    ```

    If you use it in a functional middleware, you can use it like this:

    ```py
    async def mw(request: Request, call_next: CallNext, svc: Service = inject()):
        # do something with svc
        return await call_next(request)
    ```
    """
    return cast(T, _Inject(token))

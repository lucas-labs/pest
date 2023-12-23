import re
from typing import Union

from ...utils.colorize import c


class PestException(Exception):
    """Base class for all exceptions raised by Pest during setup

    This exception is not meant to be used outside of pest's internals, since it's not
    handled by any of the asgi exception handlers.
    """

    def __init__(
        self,
        *args: object,
        hint: Union[str, None] = None,
    ):
        if hint is not None:
            hint = f'{c("🐀 Hint ⇝ ", color="light_magenta")} {hint}'
            # code `text`
            hint = re.sub(r'`([^`]+)`', lambda m: c(m.group(1), color='green'), hint)
            # bold **text**
            hint = re.sub(r'\*\*([^*]+)\*\*', lambda m: c(m.group(1), attrs=['bold']), hint)
            # underline __text__
            hint = re.sub(r'__([^_]+)__', lambda m: c(m.group(1), attrs=['underline']), hint)

        super().__init__(*(*args, hint) if hint is not None else args)

    def __str__(self) -> str:
        return '\n'.join([str(arg) for arg in self.args])

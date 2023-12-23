from typing import Dict, Iterable, Literal, Union

Color = Literal[
    'black',
    'grey',
    'red',
    'green',
    'yellow',
    'blue',
    'magenta',
    'cyan',
    'light_grey',
    'dark_grey',
    'light_red',
    'light_green',
    'light_yellow',
    'light_blue',
    'light_magenta',
    'light_cyan',
    'white',
]

Highlight = Literal[
    'on_black',
    'on_grey',
    'on_red',
    'on_green',
    'on_yellow',
    'on_blue',
    'on_magenta',
    'on_cyan',
    'on_light_grey',
    'on_dark_grey',
    'on_light_red',
    'on_light_green',
    'on_light_yellow',
    'on_light_blue',
    'on_light_magenta',
    'on_light_cyan',
    'on_white',
]

Attribute = Literal[
    'bold',
    'dark',
    'underline',
    'blink',
    'reverse',
    'concealed',
]

ATTRIBUTES: Dict[Attribute, int] = {
    'bold': 1,
    'dark': 2,
    'underline': 4,
    'blink': 5,
    'reverse': 7,
    'concealed': 8,
}

HIGHLIGHTS: Dict[Highlight, int] = {
    'on_black': 40,
    'on_grey': 40,
    'on_red': 41,
    'on_green': 42,
    'on_yellow': 43,
    'on_blue': 44,
    'on_magenta': 45,
    'on_cyan': 46,
    'on_light_grey': 47,
    'on_dark_grey': 100,
    'on_light_red': 101,
    'on_light_green': 102,
    'on_light_yellow': 103,
    'on_light_blue': 104,
    'on_light_magenta': 105,
    'on_light_cyan': 106,
    'on_white': 107,
}

COLORS: Dict[Color, int] = {
    'black': 30,
    'grey': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'light_grey': 37,
    'dark_grey': 90,
    'light_red': 91,
    'light_green': 92,
    'light_yellow': 93,
    'light_blue': 94,
    'light_magenta': 95,
    'light_cyan': 96,
    'white': 97,
}

RESET = '\033[0m'


def c(
    text: object,
    color: Union[Color, None] = None,
    on_color: Union[Highlight, None] = None,
    attrs: Union[Iterable[Attribute], None] = None,
    no_color: bool = False,
) -> str:
    result = str(text)
    if no_color:
        return result

    fmt_str = '\033[%dm%s'
    if color is not None:
        result = fmt_str % (COLORS[color], result)

    if on_color is not None:
        result = fmt_str % (HIGHLIGHTS[on_color], result)

    if attrs is not None:
        for attr in attrs:
            result = fmt_str % (ATTRIBUTES[attr], result)

    result += RESET

    return result

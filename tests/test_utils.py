from pest.core.module import setup_module as _setup_module
from pest.utils.colorize import c
from pest.utils.module import _get_provider_name, as_tree

from .cfg.pest_primitives import FooModule


def test_colorize_text():
    """🐀 utils :: colorize :: should return a colored string"""
    colored = (
        f'🤠 >'
        f'{c("Howdy", on_color="on_green")}'
        f',{c("Cowboy", color="blue", attrs=["bold", "reverse"])}!'
    )
    assert colored == '🤠 >\x1b[42mHowdy\x1b[0m,\x1b[7m\x1b[1m\x1b[34mCowboy\x1b[0m!'


def test_colorize_no_color_option():
    """🐀 utils :: colorize :: should return the original string if color option is False"""
    colored = f'🤠 > Howdy, {c("Cowboy", color="blue", attrs=["bold", "reverse"], no_color=True)}!'
    assert colored == '🤠 > Howdy, Cowboy!'


def test_module_tree_generation():
    """🐀 utils :: module :: should generate a tree representation of a module"""
    module = _setup_module(FooModule)

    tree = as_tree(module)

    assert tree == (
        '\x1b[4m\x1b[32mFooModule\x1b[0m 🐀\n    │\n    │\x1b[35m ○ ProviderBaz\x1b[0m\n    '
        '│\x1b[34m □ FooController\x1b[0m\n    ├─ Mod\n        │\x1b[35m ○ ProviderFoo\x1b[0m\n'
        '        │\x1b[35m ○ ProviderBar\x1b[0m\n'
    )

    class Foo:
        provide = 'Bar'

    # test with str injection token
    tree = _get_provider_name(Foo)
    assert tree == 'Bar'

from dataclasses import dataclass

import pytest

from pest.core.module import setup_module as _setup_module
from pest.exceptions.http.http import exc_response
from pest.metadata.meta import get_meta, get_meta_value
from pest.utils.colorize import c
from pest.utils.decorators import meta
from pest.utils.module import _get_provider_name, as_tree

from .cfg.test_modules.pest_primitives import FooModule


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


@pytest.mark.asyncio
async def test_module_tree_generation():
    """🐀 utils :: module :: should generate a tree representation of a module"""
    module = await _setup_module(FooModule)

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


def test_meta_docorator_dict_meta():
    """🐀 utils :: `meta` decorator :: should inject dict metadata into a class"""

    @dataclass
    class QuuxMeta:
        foo: str
        baz: str

    @meta({'foo': 'bar', 'baz': 'qux'})
    class Quux:
        pass

    metadata = get_meta(Quux)
    foo_value = get_meta_value(Quux, 'foo', None)
    baz_value = get_meta_value(Quux, 'baz', None)

    assert foo_value == 'bar'
    assert baz_value == 'qux'
    assert metadata == {'foo': 'bar', 'baz': 'qux'}

    meta_as_dataclass = get_meta(Quux, QuuxMeta)
    assert isinstance(meta_as_dataclass, QuuxMeta)
    assert meta_as_dataclass.foo == 'bar'
    assert meta_as_dataclass.baz == 'qux'


def test_meta_docorator_dataclass_meta():
    """🐀 utils :: `meta` decorator :: should inject dataclass metadata into a class"""

    @dataclass
    class QuuxMeta:
        foo: str
        baz: str

    @meta(QuuxMeta(foo='foo', baz='baz'))
    class Quux:
        pass

    metadata = get_meta(Quux, QuuxMeta)
    assert isinstance(metadata, QuuxMeta)
    assert metadata.foo == 'foo'
    assert metadata.baz == 'baz'

    foo_value = get_meta_value(Quux, 'foo', None)
    baz_value = get_meta_value(Quux, 'baz', None)

    assert foo_value == 'foo'
    assert baz_value == 'baz'
    metadata = get_meta(Quux)
    assert metadata == {'foo': 'foo', 'baz': 'baz'}


def test_exception_example_generator():
    """
    🐀 utils :: `exc_response` :: should generate the right example response for a given error code
    """

    example = exc_response(404, 418)

    not_found = example[404]
    assert not_found['description'] == 'Not Found'
    assert not_found['content']['application/json']['example'] == {
        'code': 404,
        'message': 'Detailed error message',
        'error': 'Not Found',
    }

    tea_pot = example[418]
    assert tea_pot['description'] == "I'm a teapot"
    assert tea_pot['content']['application/json']['example'] == {
        'code': 418,
        'message': 'Detailed error message',
        'error': "I'm a teapot",
    }

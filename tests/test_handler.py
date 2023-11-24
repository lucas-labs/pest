from pest.decorators.handler import delete, get, head, options, patch, post, put, trace
from pest.metadata.meta import META_KEY
from pest.metadata.types._meta import PestType


def test_get_handler():
    """🐀 handlers :: @get :: should make the decorated method an http handler"""

    @get('/foo')
    def foo_handler() -> str:
        return 'foo'

    assert hasattr(foo_handler, META_KEY)
    meta = getattr(foo_handler, META_KEY)
    assert meta['meta_type'] == PestType.HANDLER
    assert meta['methods'] == ['GET']


def test_post_handler():
    """🐀 handlers :: @post :: should make the decorated method an http handler"""

    @post('/foo')
    def foo_handler() -> str:
        return 'foo'

    assert hasattr(foo_handler, META_KEY)
    meta = getattr(foo_handler, META_KEY)
    assert meta['meta_type'] == PestType.HANDLER
    assert meta['methods'] == ['POST']


def test_put_handler():
    """🐀 handlers :: @put :: should make the decorated method an http handler"""

    @put('/foo')
    def foo_handler() -> str:
        return 'foo'

    assert hasattr(foo_handler, META_KEY)
    meta = getattr(foo_handler, META_KEY)
    assert meta['meta_type'] == PestType.HANDLER
    assert meta['methods'] == ['PUT']


def test_delete_handler():
    """🐀 handlers :: @delete :: should make the decorated method an http handler"""

    @delete('/foo')
    def foo_handler() -> str:
        return 'foo'

    assert hasattr(foo_handler, META_KEY)
    meta = getattr(foo_handler, META_KEY)
    assert meta['meta_type'] == PestType.HANDLER
    assert meta['methods'] == ['DELETE']


def test_patch_handler():
    """🐀 handlers :: @patch :: should make the decorated method an http handler"""

    @patch('/foo')
    def foo_handler() -> str:
        return 'foo'

    assert hasattr(foo_handler, META_KEY)
    meta = getattr(foo_handler, META_KEY)
    assert meta['meta_type'] == PestType.HANDLER
    assert meta['methods'] == ['PATCH']


def test_head_handler():
    """🐀 handlers :: @head :: should make the decorated method an http handler"""

    @head('/foo')
    def foo_handler() -> str:
        return 'foo'

    assert hasattr(foo_handler, META_KEY)
    meta = getattr(foo_handler, META_KEY)
    assert meta['meta_type'] == PestType.HANDLER
    assert meta['methods'] == ['HEAD']


def test_options_handler():
    """🐀 handlers :: @options :: should make the decorated method an http handler"""

    @options('/foo')
    def foo_handler() -> str:
        return 'foo'

    assert hasattr(foo_handler, META_KEY)
    meta = getattr(foo_handler, META_KEY)
    assert meta['meta_type'] == PestType.HANDLER
    assert meta['methods'] == ['OPTIONS']


def test_trace_handler():
    """🐀 handlers :: @trace :: should make the decorated method an http handler"""

    @trace('/foo')
    def foo_handler() -> str:
        return 'foo'

    assert hasattr(foo_handler, META_KEY)
    meta = getattr(foo_handler, META_KEY)
    assert meta['meta_type'] == PestType.HANDLER
    assert meta['methods'] == ['TRACE']

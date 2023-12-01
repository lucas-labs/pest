from fastapi.testclient import TestClient

from pest.core.application import PestApplication


def test_request_scoped_provider(di_app_n_client: tuple[PestApplication, TestClient]) -> None:
    """🐀 di :: scoped :: scoped services should act as singletons for the lifetime of a request"""
    _, client = di_app_n_client

    r1 = client.get('/scopes/scoped')
    r2 = client.get('/scopes/scoped')

    # ids comming from a user defined header inside a middleware with an
    # injected scoped service
    r1_head = r1.headers['Scoped-Id']
    r2_head = r2.headers['Scoped-Id']

    r1_ids = list(r1.json()) + [r1_head]
    r2_ids = list(r2.json()) + [r2_head]

    # assert that all ids in r1 are the same
    assert len(set(r1_ids)) == 1
    # assert that all ids in r2 are the same
    assert len(set(r2_ids)) == 1

    # assert that the ids in r1 and r2 are different (different requests)
    assert r1_head != r2_head


def test_singletons_doent_change(di_app_n_client: tuple[PestApplication, TestClient]) -> None:
    """🐀 di :: singleton ::
    scoped services should act as singletons for the lifetime of a request
    """
    _, client = di_app_n_client

    r1 = client.get('/scopes/singleton')
    r2 = client.get('/scopes/singleton')

    # ids comming from a user defined header inside a middleware with an
    # injected scoped service
    r1_head = r1.headers['Singleton-Id']
    r2_head = r2.headers['Singleton-Id']

    r1_ids = list(r1.json()) + [r1_head]
    r2_ids = list(r2.json()) + [r2_head]

    # assert that all ids in r1 are the same
    assert len(set(r1_ids)) == 1
    # assert that all ids in r2 are the same
    assert len(set(r2_ids)) == 1

    # assert that the ids in r1 and r2 are the same across requests
    assert r1_head == r2_head


def test_transient_always_new_instance(di_app_n_client: tuple[PestApplication, TestClient]) -> None:
    """🐀 di :: transient :: transient services should always return a new instance"""
    _, client = di_app_n_client

    r1 = client.get('/scopes/transient')
    r2 = client.get('/scopes/transient')

    # ids comming from a user defined header inside a middleware with an
    # injected scoped service
    r1_head = r1.headers['Transient-Id']
    r2_head = r2.headers['Transient-Id']

    r1_ids = list(r1.json()) + [r1_head]
    r2_ids = list(r2.json()) + [r2_head]

    # assert that all ids in r1 are the different
    assert len(set(r1_ids)) == len(r1_ids)
    # assert that all ids in r2 are the different
    assert len(set(r2_ids)) == len(r2_ids)

    # assert that the ids in r1 and r2 are different (different requests)
    assert r1_head != r2_head

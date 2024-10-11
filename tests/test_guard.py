import sys
from base64 import b64encode

import pytest


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info < (3, 9), reason='requires python3.9 or higher')
async def test_guards_annotated(guards_annotated_app) -> None:
    """🐀 guard :: annotated :: should run guards to decide if can activate route (>=3.9)"""

    _, client = guards_annotated_app

    admin_token = b64encode('{"id": 1, "name": "John Doe", "role": "admin"}'.encode()).decode()
    user_token = b64encode('{"id": 1, "name": "Jane Doe", "role": "user"}'.encode()).decode()

    ok = client.get('/secure', headers={'Authorization': admin_token}).json()
    assert ok == {'message': "You're allowed to see this because your role is admin"}

    forb = client.get('/secure', headers={'Authorization': user_token})
    assert forb.status_code == 403
    assert forb.json() == {'code': 403, 'error': 'Forbidden', 'message': 'Not authorized'}

    unauth = client.get('/secure')
    assert unauth.status_code == 401
    assert unauth.json() == {'code': 401, 'error': 'Unauthorized', 'message': 'Token is required'}


@pytest.mark.asyncio
async def test_guards_typed(guards_annotated_app) -> None:
    """🐀 guard :: typed :: should run guards to decide if can activate route (>=3.8)"""

    _, client = guards_annotated_app

    admin_token = b64encode('{"id": 1, "name": "John Doe", "role": "admin"}'.encode()).decode()
    user_token = b64encode('{"id": 1, "name": "Jane Doe", "role": "user"}'.encode()).decode()

    ok = client.get('/secure/typed', headers={'Authorization': admin_token}).json()
    assert ok == {'message': "You're allowed to see this because your role is admin"}

    forb = client.get('/secure/typed', headers={'Authorization': user_token})
    assert forb.status_code == 403
    assert forb.json() == {'code': 403, 'error': 'Forbidden', 'message': 'Not authorized'}

    unauth = client.get('/secure/typed')
    assert unauth.status_code == 401
    assert unauth.json() == {'code': 401, 'error': 'Unauthorized', 'message': 'Token is required'}

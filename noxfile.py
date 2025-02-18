from nox_poetry import Session, session


@session(python=['3.13', '3.12', '3.11', '3.10', '3.9'])
def tests(session: Session) -> None:
    session.install(
        '.',
        'colorama',
        'pytest-cov',
        'loguru',
        'croniter',
        'pytest',
        'httpx',
        'pytest-asyncio',
        'python-multipart',
    )

    params = (
        ['--cov=pest', 'tests/', '--cov-report=xml'] if session.python == '3.11' else ['tests/']
    )

    session.run('pytest', *params)

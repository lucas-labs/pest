from nox_poetry import Session, session


@session(
    python=[
        '3.12',
        '3.11',
        '3.10',
        '3.9',
        '3.8',
    ]
)
def tests(session: Session) -> None:
    session.install(
        '.',
        'colorama',
        'pytest-cov',
        'loguru',
        'pytest',
        'httpx',
        'pytest',
        'pytest-asyncio',
    )

    params = (
        ['--cov=pest', 'tests/', '--cov-report=xml'] if session.python == '3.11' else ['tests/']
    )

    session.run('pytest', *params)

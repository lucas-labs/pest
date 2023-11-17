import re
from typing import Any

from loguru import logger

from pest import Pest
from pest.logging import LogLevel

from .app_module import AppModule


def format_record(record: Any) -> str:
    # strip ANSI escape sequences
    format_string = '<green>{time}</green> <level>{message}</level>\n'
    ansi_escape = re.compile(r'\x1B\[\d+(;\d+){0,2}m')
    record['message'] = ansi_escape.sub('', record['message'])
    return format_string


app = Pest.create(
    AppModule,
    logging={
        'intercept': [('uvicorn*', LogLevel.DEBUG), 'pest*', 'fastapi'],
        'level': LogLevel.DEBUG,
        'access_log': True,
        'sinks': [{
            'sink': 'example/logs/app.log',
            'rotation': '1 week',
            'format': format_record
        }],
    }
)

logger.info(f'App started:\n\n{app}')

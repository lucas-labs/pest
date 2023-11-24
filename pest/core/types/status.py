from enum import Enum


class Status(str, Enum):
    """Status of a pest primitive"""

    NOT_SETUP = 'NOT_SETUP'
    SETTING_UP = 'SETTING_UP'
    READY = 'READY'

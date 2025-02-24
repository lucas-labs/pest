"""
Module providing typed dicts for the metadata CronMeta:
- pest/schedule/decorators/types/cron_meta.py

ATTENTION:
This file was auto-generated by `task gen:types`.
Do not edit manually.
"""

from typing import TypedDict, Union


class CronMetaDict(TypedDict, total=False):
    max_repetitions: Union[int, None]
    '''🐀 ⇝ maximum number of repetitions'''

    name: Union[str, None]
    '''🐀 ⇝ name of the cron job'''

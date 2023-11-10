from typing import Unpack

from fastapi import FastAPI

from .types.fastapi_params import FastAPIParams


class PestApplication(FastAPI):
    """🐀 ⇝ what a pest!"""

    def __init__(self, *, x: int, **kwargs: Unpack[FastAPIParams]) -> None:
        super().__init__(**kwargs)

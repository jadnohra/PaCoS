import multiprocessing
from typing import Any


def create_parall_context() -> Any:
    return multiprocessing.get_context('spawn')
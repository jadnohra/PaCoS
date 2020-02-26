from typing import Any
from .interfaces import Address


class ProcCall:
    def __init__(self, target: Address, payload: Any = None):
        super().__init__()
        self._target = target
        self._payload = payload

    def __str__(self) -> str:
        return '{} -> {}'.format(self._payload, self._target)

    @property
    def target(self) -> Address:
        return self._target
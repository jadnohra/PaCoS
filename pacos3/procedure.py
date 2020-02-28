import logging
from .interfaces import IProcedure, ProcState, Token, Time


class Procedure(IProcedure):
    def __init__(self, name: str, state: ProcState):
        self._name = name
        self._state = state

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> ProcState:
        return self._state

    @state.setter
    def state(self, state: ProcState) -> None:
        self._state = state

    def __str__(self) -> str:
        return '{} ({})'.format(self.name, self.state)
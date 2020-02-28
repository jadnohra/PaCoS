import logging
from .interfaces import (
            IProcedure, ProcState, Token, IProcessorState, CallResult)


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

    def call(self, token: Token, processor: IProcessorState) -> CallResult:
        return CallResult()

    def __str__(self) -> str:
        return '{} ({})'.format(self.name, self.state)
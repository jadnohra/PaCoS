import logging
from .interfaces import IProcedure, ProcState, Token, Time, CallMode


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

    def should_process(self, token: Token, time: Time, mode: CallMode) -> bool:
        if mode.use_proc_state:
            if self.state == ProcState.CLOSED:
                logging.debug("{}: Called while closed : {}".format(
                              self, token))
                return False
            elif self.state == ProcState.DROPPING:
                return False
        return True
    
    def __str__(self) -> str:
        return '{} ({})'.format(self.name, self.state)
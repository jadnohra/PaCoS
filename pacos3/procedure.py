import logging
from .interfaces import IProcedure, ProcState, ProcCall


class Procedure(IProcedure):
    def __init__(self, name: str, state: ProcState):
        self._state = state

    @property
    def state(self) -> ProcState:
        return self._state

    @state.setter
    def state(self, state: ProcState) -> None:
        self._state = state

    def can_process(self, call: ProcCall) -> bool:
        logging.debug(call)
        if self.state == ProcState.CLOSED:
            logging.debug("{}: Called while closed : {}".format(
                          self, call))
            return False
        return True
    
    def __str__(self) -> str:
        return '{} ({})'.format(self.name, self.state)
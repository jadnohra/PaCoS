import logging
from .interfaces import IPin, PinState, IMessage, IMsgRouter


class PinBase(IPin):
    def __init__(self, name: str, state: PinState):
        self._name = name
        self._state = state

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> PinState:
        return self._state

    def can_process(self) -> bool:
        if self.state == PinState.CLOSED:
            logging.error("{}: Received message while closed".format(self))
            return False
        return True
    
    def __repr__(self) -> str:
        return '{} ({})'.format(self.address, self.state)
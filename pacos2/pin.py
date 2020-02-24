import logging
from .interfaces import IPin, PinState, IMessage, IMsgRouter
from .addressable import Addressable


class PinBase(IPin):
    def __init__(self, name: str, state: PinState):
        Addressable.__init__(self, name)
        self._state = state

    @property
    def state(self) -> PinState:
        return self._state

    @state.setter
    def state(self, state: PinState) -> None:
        self._state = state

    def can_process(self, msg: IMessage) -> bool:
        logging.debug(msg)
        if self.state == PinState.CLOSED:
            logging.error("{}: Received message while closed : {}".format(
                          self, msg))
            return False
        return True
    
    def __repr__(self) -> str:
        return '{} ({})'.format(self.address, self.state)
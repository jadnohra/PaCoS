import logging
from typing import List
from ..interfaces import Time, IMessage, PinState, Address, IMsgRouter
from ..pin import PinBase


class BufferPin(PinBase):
    def __init__(self, name: str, state: PinState, processing_time: int = 1):
        super().__init__(name, state)
        self._processing_time = processing_time
        self._buffer = []

    @property
    def messages(self) -> List[IMessage]:
        return self._buffer

    def process(self, msg: IMessage, msg_router: IMsgRouter) -> Time:
        if self.state == PinState.CLOSED:
            logging.error("{}: Received message while closed".format(self))
        self._buffer.append(msg)
        return self._processing_time

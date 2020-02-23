import logging
from ..interfaces import Time, IMessage, PinState, IMsgRouter
from ..pin import PinBase


class NullPin(PinBase):
    def __init__(self, name: str, state: PinState, processing_time: int = 1):
        super().__init__(name, state)
        self._processing_time = processing_time

    def process(self, msg: IMessage, msg_router: IMsgRouter) -> Time:
        if self.state == PinState.CLOSED:
            logging.error("{}: Received message while closed".format(self))
        return self._processing_time

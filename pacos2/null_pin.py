import logging
from .interfaces import Time, IMessage, PinState
from .pin import PinBase


class NullPin(PinBase):
    def __init__(self, processing_time: int = 1):
        self._processing_time = processing_time

    def process(self, msg: IMessage) -> Time:
        if self.state == PinState.CLOSED:
            logging.error("{}: Received message while closed".format(self))
        return self._processing_time

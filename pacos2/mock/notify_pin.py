import logging
from typing import Callable
from ..interfaces import Time, IMessage, PinState, IMsgRouter
from ..pin import PinBase


class NotifyPin(PinBase):
    def __init__(self, name: str, state: PinState, 
                 notif_func: Callable[None, [NotifyPin, IMessage, IMsgRouter]],
                 processing_time: int = 1):
        super().__init__(name, state)
        self._processing_time = processing_time
        self._notif_func = notif_func

    def process(self, msg: IMessage, msg_router: IMsgRouter) -> Time:
        if self.state == PinState.CLOSED:
            logging.error("{}: Received message while closed".format(self))
        self._notif_func(self, msg, msg_router)
        return self._processing_time

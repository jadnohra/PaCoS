import logging
from ..interfaces import Time, IMessage, PinState, Address, IMsgRouter
from ..pin import PinBase


class IdentPin(PinBase):
    def __init__(self, name: str, state: PinState, out_address: Address, 
                 processing_time: int = 1):
        super().__init__(name, state)
        self._out_address = out_address
        self._processing_time = processing_time

    def process(self, msg: IMessage, msg_router: IMsgRouter) -> Time:
        if self.state == PinState.CLOSED:
            logging.error("{}: Received message while closed".format(self))
        msg.forward(self._out_address)
        msg_router.route(msg)
        return self._processing_time

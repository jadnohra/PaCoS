import logging
from typing import List, Callable
from ..interfaces import Time, IPin, IMessage, PinState, Address, IMsgRouter
from ..pin import PinBase


class NullPin(PinBase):
    def __init__(
          self, name: str, state: PinState, 
          notif_func: Callable[None, [IPin, IMessage, IMsgRouter]] = None,
          processing_time: int = 1):
        super().__init__(name, state)
        self._notif_func = notif_func
        self._processing_time = processing_time

    def process(self, msg: IMessage, router: IMsgRouter) -> Time:
        if not super().can_process():
            return 0
        if self._notif_func:
            self._notif_func(self, msg, router)
        return self._processing_time


class IdentPin(PinBase):
    def __init__(
          self, name: str, state: PinState, out_address: Address, 
          notif_func: Callable[None, [IPin, IMessage, IMsgRouter]] = None,
          processing_time: int = 1):
        super().__init__(name, state)
        self._out_address = out_address
        self._notif_func = notif_func
        self._processing_time = processing_time

    def process(self, msg: IMessage, router: IMsgRouter) -> Time:
        if not super().can_process():
            return 0
        if self._notif_func:
            self._notif_func(self, msg, router)
        msg.forward(self._out_address)
        router.route(msg)
        return self._processing_time


class BufferPin(PinBase):
    def __init__(
          self, name: str, state: PinState, 
          notif_func: Callable[None, [IPin, IMessage, IMsgRouter]] = None,
          processing_time: int = 1):
        super().__init__(name, state)
        self._processing_time = processing_time
        self._notif_func = notif_func
        self._buffer = []

    @property
    def messages(self) -> List[IMessage]:
        return self._buffer

    def process(self, msg: IMessage, router: IMsgRouter) -> Time:
        if not super().can_process():
            return 0
        self._buffer.append(msg)
        if self._notif_func:
            self._notif_func(self, msg, router)
        return self._processing_time